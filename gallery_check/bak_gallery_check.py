import sys
import re
import requests
import logging
import random
import string
from os import listdir
from random import choice

logging.basicConfig(level=logging.INFO, format=u'[%(asctime)s] %(message)s', filename=u'gallery_checker.log')
STATUS_CHECKER_ERROR = 1
STATUS_SERVICE_MUMBLE = 2
STATUS_SERVICE_CORRUPT = 3
STATUS_SERVICE_DOWN = 4


class ServiceMumbleException(Exception):
    pass


class ServiceCorruptException(Exception):
    pass


class ServiceDownException(Exception):
    pass


class NonImplementedException(Exception):
    pass


class Action():
    def __init__(self, host, port):
        self.url_base = "http://" + str(host) + ":" + str(port)
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}
        logging.info('working with %s', self.url_base)

    def create_user(self, name, password):
        url = self.url_base + "/register"
        logging.info('creating new user %s:%s on host %s:', name, password, self.url_base)
        self.status = 0
        try:
            response = requests.post(
                url,
                params={
                    'username': str(name),
                    'password1': str(password),
                    'password2': str(password)
                },
                headers=self.headers
            )
            self.status = response.status_code
        except:
            pass

        if self.status == 200:
            logging.info('new user %s:%s on host %s: created, %s', name, password, self.url_base, self.status)
            return dict(response.request._cookies)
        else:
            logging.info('failed to create new user %s:%s on host %s, status %s', name, password, self.url_base,
                         self.status)
            return None

    def login_chk(self, name, password):
        url = self.url_base + "/login"
        logging.info('trying to login %s:%s on host %s', name, password, self.url_base)
        self.status = 0
        try:
            response = requests.post(
                url,
                params={
                    'username': str(name),
                    'password': str(password)
                },
                headers=self.headers
            )
            self.status = response.status_code
        except:
            pass

        if self.status == 200:
            logging.info('login %s:%s on host %s: success, %s', name, password, self.url_base, self.status)
            return dict(response.request._cookies)
        else:
            logging.info('failed to login user %s:%s on host %s, status %s', name, password, self.url_base, self.status)
        return None

    def add_flag(self, cookies, flag, title, text):
        append = "/add"
        return self.edit_flag(cookies, flag, title, text, append)

    def edit_flag(self, cookies, flag, title, text, apend_url):
        url = self.url_base + apend_url
        self.status = 0
        try:
            filename = choice(listdir('./images/'))
            f = open("./images/" + filename)
        except:
            f = None
        try:
            if f:
                response = requests.post(
                    url,
                    params={
                        'title': str(title),
                        'text': str(text),
                        'notes': str(flag),
                    },
                    files={'file': f},
                    headers=self.headers,
                    cookies=cookies
                )
                self.status = response.status_code
            else:
                response = requests.post(
                    url,
                    params={
                        'title': str(title),
                        'text': str(text),
                        'notes': str(flag),
                    },
                    headers=self.headers,
                    cookies=cookies
                )
                self.status = response.status_code
        except:
            pass
        if self.status == 200:
            logging.info('put flag %s to host %s: %s', flag, self.url_base, self.status)
            return self.status
        else:
            logging.info('failed to put flag %s to host %s: %s', flag, self.url_base, self.status)
            return None

    def check_flag(self, cookies, flag):
        url = self.url_base + "/"
        self.status = 0
        try:
            response = requests.get(
                url,
                headers=self.headers,
                cookies=cookies
            )
            self.status = response.status_code
            if str(flag) in response.text:
                return flag
        except:
            pass
        return None

    def get_flag(self, cookies):
        url = self.url_base + "/myposts"
        try:
            response = requests.get(
                url,
                headers=self.headers,
                cookies=cookies
            )
            self.status = response.status_code
            str = response.text.strip("\n").replace('\n', '')
            return re.findall(u'</span>(.+?)<p ', str)[0]
        except:
            pass
        return None

    def knock_Knock(self, path, cookies):
        url = self.url_base + path
        self.status = 0
        try:
            response = requests.get(
                url,
                headers=self.headers,
                cookies=cookies
            )
            self.status = response.status_code
        except:
            pass

        if self.status != 200:
            return None
        return self.status

    def getMyPostId(self, cookies):
        url = self.url_base + "/"
        try:
            response = requests.get(
                url,
                headers=self.headers,
                cookies=cookies
            )
            self.status = response.status_code
            str = response.text.strip("\n").replace('\n', '')
            return re.findall(u'/edit/(.+?)">', str)[0]
        except:
            pass
        return None

    def addComment(self, cookies, id, text):
        url = self.url_base + "/post/" + id
        self.status = 0
        try:
            response = requests.post(
                url,
                params={
                    'id': str(id),
                    'text': str(text),
                },
                headers=self.headers,
                cookies=cookies
            )
            self.status = response.status_code
        except:
            pass

        if self.status == 200:
            return self.status
        else:
            return None


def putFlag(host, port, flag):
    action = Action(str(host), str(port))

    username = ''.join(random.choice(string.ascii_lowercase) for x in range(16))
    userpass = ''.join(random.choice(string.ascii_lowercase) for x in range(16))
    logging.info('try to add flag to %s user=%s pass=%s', action.url_base, username, userpass)

    cookies_register = action.create_user(username, userpass)
    cookies_auth = action.login_chk(username, userpass)
    if not cookies_register:
        raise ServiceCorruptException

    if not cookies_auth:
        raise ServiceCorruptException

    state = action.add_flag(cookies_auth, str(flag), ''.join(random.choice(string.ascii_lowercase) for x in range(16)),
                            ''.join(random.choice(string.ascii_lowercase) for x in range(16)))
    if state:
        return cookies_auth
    else:
        raise ServiceMumbleException


def getFlag(host, port, state):
    action = Action(str(host), str(port))
    flag = action.get_flag(str(state))
    if not flag:
        logging.info('some FUCK with flag getting in %s cookies=%s', action.url_base, state)
        raise ServiceCorruptException
    return flag


def chkFlag(host, port):
    action = Action(str(host), str(port))
    username = ''.join(random.choice(string.ascii_lowercase) for x in range(16))
    userpass = ''.join(random.choice(string.ascii_lowercase) for x in range(16))
    cookies_register = action.create_user(username, userpass)
    cookies_auth = action.login_chk(username, userpass)
    if not cookies_register:
        raise ServiceCorruptException

    if not cookies_auth:
        raise ServiceCorruptException

    if not action.knock_Knock("/", cookies_auth):
        raise ServiceCorruptException

    if not action.knock_Knock("/myposts", cookies_auth):
        raise ServiceCorruptException

    if not action.knock_Knock("/export", cookies_auth):
        raise ServiceCorruptException

    if not action.knock_Knock("/admin", cookies_auth):
        raise ServiceCorruptException

    if not action.knock_Knock("/export", cookies_auth):
        raise ServiceCorruptException

    text = ''.join(random.choice(string.ascii_lowercase) for x in range(16))
    action.add_flag(cookies_auth, text, "TEMP", "TEMP")

    if not action.check_flag(cookies_auth, text):
        raise ServiceMumbleException

    id = action.getMyPostId(cookies_auth)
    if not action.knock_Knock("/post/" + id, cookies_auth):
        raise ServiceCorruptException

    if not action.addComment(cookies_auth, id, text):
        raise ServiceMumbleException

    if not action.edit_flag(cookies_auth, text, text, text, "/edit/" + id):
        raise ServiceMumbleException

    if not action.knock_Knock("/delete/" + id, cookies_auth):
        raise ServiceMumbleException


if __name__ == '__main__':
    if len(sys.argv) < 3:
        exit(STATUS_CHECKER_ERROR)
    try:
        cmd = sys.argv[1]
        host = sys.argv[2]
        port = int(sys.argv[3])

        if "put" == cmd:
            if len(sys.argv) < 5:
                exit(STATUS_CHECKER_ERROR)
            flag = sys.argv[4]
            print putFlag(host, port, flag)

        elif "get" == cmd:
            if len(sys.argv) < 5:
                exit(STATUS_CHECKER_ERROR)
            state = sys.argv[4]
            print getFlag(host, port, state)

        elif "chk" == cmd:
            print chkFlag(host, port)

        else:
            exit(STATUS_CHECKER_ERROR)

    except ServiceMumbleException:
        exit(STATUS_SERVICE_MUMBLE)

    except ServiceCorruptException:
        exit(STATUS_SERVICE_CORRUPT)

    except ServiceDownException:
        exit(STATUS_SERVICE_DOWN)

    action = Action("127.0.0.1", "8000")
    # print action.create_user("bot", "botpass")
    cookies = action.login_chk("bot", "botpass")
    # print action.add_flag(cookies, "BotTestFlag2")
    # print action.check_flag(cookies, "BotTestFlag2")
    # print action.get_flag(cookies)
    # id = action.getMyPostId(cookies)