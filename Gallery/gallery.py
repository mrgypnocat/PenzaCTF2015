import concurrent.futures
import os.path
import re
import torndb
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web





from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="gallery", help="database name")
define("mysql_user", default="admin", help="database user")
define("mysql_password", default="admin", help="database password")

executor = concurrent.futures.ThreadPoolExecutor(2)

############################    MMM WHAT's time?      ###########################
############################  IT'S SHITCODE TIME1111  ###########################
admin_id = "0"
admin_name = "admin"
admin_pass = "admin"


class Application(tornado.web.Application):
    admin_id = 0
    admin_name = "admin"
    admin_pass = "admin"

    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/add", AddHandler),
            (r"/myposts", MypostsHandler),
            (r"/post/([0-9]+)", OnePostHandler),
            (r"/edit/([0-9]+)", EditHandler),
            (r"/delete/([0-9]+)", DeleteHandler),
            (r"/register", AuthCreateHandler),
            (r"/login", AuthLoginHandler),
            (r"/logout", AuthLogoutHandler),
            (r"/admin", AdminHandler),
            (r"/export", ExportHandler),
            (r"/.*", RedirectHandler),
        ]
        settings = dict(
            main_title=u"Pony Gallery",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            cookie_secret="gallery",
            login_url="/login",
            debug=True,
        )

        super(Application, self).__init__(handlers, **settings)
        # Have one global connection to DB across all handlers
        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

############################    MMM WHAT's time?      ###########################
############################  IT'S SHITCODE TIME1111  ###########################
    @property
    def user_is_admin(self):
        user_id = self.get_cookie("user")
        # user_id = self.get_secure_cookie("gallery_user")
        if int(user_id) == int(admin_id):
            return True
        else:
            return False

    def get_current_user(self):
        # user_id = self.get_secure_cookie("gallery_user")
        user_id = self.get_cookie("user")
        if not user_id:
            return None
        try:
            user = self.db.query("SELECT * FROM authors WHERE id = %s", int(user_id))[0] or None
            return user
        except:
            return None

    def get_current_user_id(self):
        # user_id = self.get_secure_cookie("gallery_user")
        user_id = self.get_cookie("user")
        if not user_id:
            return None

        if user_id == admin_id:
            return admin_id

        try:
            user = self.db.query("SELECT * FROM authors WHERE id = %s", int(user_id))[0] or None
            return user.id
        except:
            return None

    def any_author_exists(self):
        return bool(self.db.get("SELECT * FROM authors LIMIT 1"))


class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        entries = self.db.query("SELECT * FROM entries ORDER BY published DESC")
        for e in entries:
            author_name = self.db.query("SELECT name FROM authors WHERE id=%s ", e.author_id)
            comments_count = len(self.db.query("SELECT * FROM comments WHERE entry_id=%s ", e.id))
            enabled = None
            if e.author_id == self.get_current_user_id() or self.user_is_admin:
                enabled = True

            try:
                e.update(author_name[0])
            except:
                e.update({'name': "fuck"})

            e.update({'author_enabled': enabled})
            e.update({'comments': comments_count})

        self.render("home.html", entries=entries)


class MypostsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        entries = self.db.query("SELECT * FROM entries WHERE author_id=%s ORDER BY published DESC", self.get_current_user_id())
        for e in entries:
            author_name = self.db.query("SELECT name FROM authors WHERE id=%s ", e.author_id)
            comments_count = len(self.db.query("SELECT * FROM comments WHERE entry_id=%s ", e.id))
            enabled = True if e.author_id == self.get_current_user_id() or self.user_is_admin else None

            try:
                e.update(author_name[0])
            except:
                e.update({'name': "fuck"})

            e.update({'author_enabled': enabled})
            e.update({'comments': comments_count})

        self.render("home.html", entries=entries)


class AddHandler(BaseHandler):
    def get(self):
        self.render("add_item.html")

    def post(self):
        author = self.get_current_user_id() or 0
        title = self.get_argument("title", None)
        text = self.get_argument("text", None)
        hidden_text = self.get_argument("notes", None)
        try:
            file = self.request.files['file'][0] or None
        except:
            file = ""

        if file:
            file_location_inStatic = "download/"
            filepath = "static/" + file_location_inStatic + file['filename']
            output_file = open(filepath, 'w')
            output_file.write(file['body'])
            # self.finish("file " + filepath + " is uploaded")
            file = file_location_inStatic + file['filename']

        self.db.execute(
            "INSERT INTO entries (author_id, title, text, hidden_text, filepath, published)"
            "VALUES (%s,%s,%s,%s,%s,UTC_TIMESTAMP())",
            author, title, text, hidden_text, file)

        self.redirect("/")


class OnePostHandler(BaseHandler):
    def get(self, id):
        entry = self.db.get("SELECT * FROM entries WHERE id = %s", id)
        if not entry:
            raise tornado.web.HTTPError(404)

        author_name = self.db.query("SELECT name FROM authors WHERE id=%s ", entry.author_id)
        enabled = True if entry.author_id == self.get_current_user_id() or self.user_is_admin else None
        entry.update({'author_enabled': enabled})

        try:
            entry.update(author_name[0])
        except:
            entry.update({'name': "fuck"})

        comments = self.db.query("SELECT * FROM comments WHERE entry_id = %s ORDER BY published ", id) or None
        if comments:
            for c in comments:
                try:
                    author_name = self.db.query("SELECT name FROM authors WHERE id=%s ", c.author_id)
                    c.update(author_name[0])
                except:
                    c.update({'name': "fuck"})
        self.render("one_item.html", entry=entry, comments=comments)

    def post(self, id):
        id = self.get_argument("id", None)
        text = self.get_argument("text", None)
        author = self.get_current_user_id() or 0

        self.db.execute(
            "INSERT INTO comments (author_id,entry_id,text,published)"
            "VALUES (%s,%s,%s,UTC_TIMESTAMP())",
            author, id, text, )

        self.redirect("/post/" + id)


class EditHandler(BaseHandler):
    def get(self, id):
        entry = self.db.get("SELECT * FROM entries WHERE id = %s", id)
        if not entry:
            raise tornado.web.HTTPError(404)
        self.render("edit_item.html", entry=entry)

    def post(self, id):
        title = self.get_argument("title", None)
        text = self.get_argument("text", None)
        hidden_text = self.get_argument("notes", None)

        # TODO:
        real_author_id = self.db.query("SELECT author_id FROM entries WHERE id=%s ", id)
        author_id = self.get_current_user_id() or 0

        try:
            file = self.request.files['file'][0] or None
        except:
            file = None

        if file is not None:
            file_location_inStatic = "download/"
            filepath = "static/" + file_location_inStatic + file['filename']
            output_file = open(filepath, 'w')
            output_file.write(file['body'])
            # self.finish("file " + filepath + " is uploaded")
            file = file_location_inStatic + file['filename']
        else:
            try:
                self.db.execute(
                    "UPDATE entries SET title=%s, text=%s, hidden_text=%s, filepath=%s, author_id=%s WHERE id=%s",
                    title, text, hidden_text, file, author_id, id)
            except:
                pass

        self.redirect("/post/" + id)


class DeleteHandler(BaseHandler):
    def get(self, id):
        entry = self.db.get("SELECT * FROM entries WHERE id = %s", id)
        if not entry:
            raise tornado.web.HTTPError(404)
        if self.get_current_user_id() == entry.author_id or self.user_is_admin:
            self.db.execute("DELETE FROM entries WHERE id =%s", id)
        else:
            pass
        self.redirect("/")


class AdminHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("No money = no honey!")


class RedirectHandler(tornado.web.RequestHandler):
    def get(self):
        self.redirect("/")


class ExportHandler(BaseHandler):
    def get(self):
        author_id = self.get_current_user_id()
        entry_id = self.get_argument("entry", None, strip=False)
        comment_id = self.get_argument("comment", None, strip=False)

        if entry_id:
            query="SELECT * FROM entries WHERE id=" + str(entry_id) + " AND author_id="+str(author_id)
            entries = self.db.query(query)
        else:
            if (author_id == admin_id):
                entries = self.db.query("SELECT * FROM entries")
            else:
                query="SELECT * FROM entries WHERE author_id="+str(author_id)
                entries = self.db.query(query)

        if comment_id:
            query="SELECT * FROM comments WHERE id="+str(comment_id)
            comments = self.db.query(query)
            self.write("".join(str(e) for e in comments))

        self.write("".join(str(e) for e in entries))



class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("gallery_user")
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))


class AuthLoginHandler(BaseHandler):
############################    MMM WHAT's time?      ###########################
############################  IT'S SHITCODE TIME1111  ###########################
    def get(self):
        # If there are no authors, redirect to the account creation page.
        if not self.any_author_exists():
            self.redirect("/register")
        else:
            self.render("sign_in.html", error=None)

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        if username == admin_name and password == admin_pass:
            global admin_id
            self.db.execute("DELETE from authors WHERE name=%s", admin_name)
            admin_id = self.db.execute(
                "INSERT INTO authors (name, hashed_password) "
                "VALUES (%s, %s)",
                admin_name,
                admin_pass,
            )

        try:
            user = self.db.query("SELECT * FROM authors WHERE name = %s",
                                 username)[0] or None
        except:
            user = None

        if not user:
            self.render("sign_in.html", error="no such user")
            return

        if user.hashed_password != password:
            self.render("sign_in.html", error="wrong password")
            return
        else:
            self.set_secure_cookie("gallery_user", str(user.id))
            self.set_cookie("user", str(user.id))
            self.redirect(self.get_argument("next", "/"))
            return


class AuthCreateHandler(BaseHandler):
    def get(self):
        self.render("register.html", error=None)

    def post(self):
        # if self.any_author_exists():
        #   self.render("register.html", error="")
        #   return
        pass1 = self.get_argument("password1")
        pass2 = self.get_argument("password2")
        if pass1 == pass2:
            user = self.db.execute(
                "INSERT INTO authors (name, hashed_password) "
                "VALUES (%s, %s)",
                self.get_argument("username"),
                pass1,
            )
            self.set_secure_cookie("gallery_user", str(user))
            self.set_cookie("user", str(user))
            self.redirect("/")
        else:
            self.render("register.html", error="Passwords mistmatch")


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
