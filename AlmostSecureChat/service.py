# -*- coding: utf-8 -*-
#!/usr/bin/env python3

#imports
from socket import socket
from peewee import *
from time import strftime, sleep
from threading import Thread, current_thread
from collections import namedtuple
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256

import binascii

#globals
db = SqliteDatabase('database.db')
PORT = 33333
ADDRESS = '127.0.0.1'

Command = namedtuple("Command",
    "command user pub_key priv_key data_id data signature")


#functions
def log(message):

    log_message = str(str(strftime("[%d %b %Y %H:%M:%S] ("))
                      + current_thread().name + ") " + str(message) + "\n")
    print(log_message, end="")


def Parse(data):
    commands = ['?', 'register', 'insert', 'select', 'get']
    message = Command(command="", user="", pub_key="",
        priv_key="", data_id="", data="", signature="")
    tmp = str(data).replace('\n', '').replace('\\n', '').replace("b'", '') \
        .replace("'", "").replace('b"', '').replace('"', '').split(' ')
		
    for i in commands:
        if tmp[0].find(i) != -1:
            message = message._replace(command=i)
            break
    if (message.command == 'insert'):
        message = message._replace(user=tmp[1])
        message = message._replace(data=tmp[2])
        message = message._replace(data_id=tmp[3])
        message = message._replace(signature=tmp[4])
    elif (message.command == 'select'):
        message = message._replace(user=tmp[1])
        message = message._replace(data_id=tmp[2])
        message = message._replace(signature=tmp[3])
    elif (message.command == 'register'):
        message = message._replace(user=tmp[1])
    elif (message.command == 'get'):
        message = message._replace(user=tmp[1])
    else:
        message = message._replace(command="?")

    return message


#classes
class User(Model):
    name = CharField(unique=True)
    ip = CharField()
    PubKey = CharField(unique=True)

    class Meta:
        database = db


class Data(Model):
    owner = ForeignKeyField(User, related_name='teams')
    data_id = CharField()
    data = CharField()

    class Meta:
        database = db


class DataBaseConnector():

    def __init__(self):
        db.create_tables([User, Data], True)

    def __enter__(self):
        db.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        db.close()

    def InsertData(self, user, user_ip, user_pub_key, data, data_id):
        with db.transaction():
            (userRec, created) = User.get_or_create(name=user,
                                                    ip=user_ip,
                                                    PubKey=user_pub_key)
            userRec.save()
            (dataRec, created) = Data.get_or_create(owner=userRec,
                                                    data_id=data_id,
                                                    defaults={'data': data})
            dataRec.data = data
            dataRec.save()

    def SelectData(self, user, data_id):
        print(user, data_id)
        with db.transaction():
            try:
                query = Data.select(Data, User).join(User).where(
                    (User.name == user) & (Data.data_id == data_id))
                return str(query[0].data)
            except Exception as ex:
                return(str('Failed to get data due to the reason: {0}'.format(ex)))

    def GetUserKey(self, user):
        with db.transaction():
            try:
                query = User.select(User).where((User.name == user))
                return str(query[0].PubKey), str(query[0].ip)
            except Exception as ex:
                return(str('Failed to get data due to the reason: {0}'.format(ex)))

    def RegisterUser(self, user, user_ip, user_pub_key):
        with db.transaction():
            (userRec, created) = User.get_or_create(name=user,
                                                    ip=user_ip,
                                                    PubKey=user_pub_key)
            userRec.save()


class ServerThread(Thread):

    def __init__(self, conn, addr):

            Thread.__init__(self)
            self.conn = conn
            self.addr = addr

    # взаимодействие с клиентом
    def user_interaction(self, conn, addr):

        self.conn.sendall('This is Almost Secure Chat.\n'.encode('utf-8'))

        self.conn.sendall('Enter your command ("?" for help):\n'.encode('utf-8'))
        while True:
            data = self.conn.recv(1024)  # максимальный размер сообщения
            if not data:
                log('no command from ' + str(self.addr))
                return
            break
        log('got data ' + str(data) + ' from ' + str(self.addr))

        message = Parse(data)
        Random.seed()
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)

        connector = DataBaseConnector()

        if (message.command == 'insert'):
            # check sign
            user_pub_key, user_ip = connector.GetUserKey(message.user)
            data_string = message.command + message.user + message.data \
                 + message.data_id
            hash = SHA256.new()
            hash.update(data_string.encode("utf-8"))
            hash_string = hash.digest()
            wow = RSA.importKey(user_pub_key)
            emsg = wow.decrypt(binascii.unhexlify(message.signature))
            if (emsg == hash_string):
                connector.InsertData(message.user, str(self.addr[0]),
                                user_pub_key, message.data, message.data_id)
                answer = "Data inserted\n"
            else:
                answer = "Wrong signature\n"

        elif (message.command == 'select'):
            # check sign
            user_pub_key, user_ip = connector.GetUserKey(message.user)
            data_string = message.command + message.user + message.data_id
            hash = SHA256.new()
            hash.update(data_string.encode("utf-8"))
            hash_string = hash.digest()
            wow = RSA.importKey(user_pub_key)
            emsg = wow.decrypt(binascii.unhexlify(message.signature))
            if (emsg == hash_string):
                answer = connector.SelectData(message.user, message.data_id)
            else:
                answer = "Wrong signature\n"

        elif (message.command == 'register'):
            user_pub_key = key.publickey().exportKey("PEM")
            user_private_key = key.exportKey("PEM")
            connector.RegisterUser(message.user,
                str(self.addr[0]),
                user_private_key)
            answer = 'Register OK. Your keys is\n Public Key: ' + \
                str(user_pub_key) + ' \n Private Key: ' + str(user_private_key)

        elif (message.command == 'get'):
            user_pub_key, user_ip = connector.GetUserKey(message.user)
            answer = user_pub_key + "\n" + user_ip

        elif (message.command == '?'):
            answer = "Usage: \n register <username>\n insert <username> " + \
                "<data> <data_id> <signature>\n select <username> " + \
                "<data_id> <signature>\n get <username> \n"
        else:
            anwer = "Unknown command"
        print(answer)
        # pack message
        self.conn.sendall(answer.encode('utf-8'))

    def run(self):

        try:
            log('Started ServerThread with ' + str(self.addr))
            self.user_interaction(self.conn, self.addr)
        except Exception as e:
            log("ending work with error: " + str(e) + ' to ' + str(self.addr))
        finally:
            log('ending work with ' + str(self.addr))
            self.conn.close()


class Wait(Thread):

    def __init__(self, sock):
        Thread.__init__(self)
        self.game_sock = sock

    def run(self):
        while (True):
            conn, addr = self.game_sock.accept()
            log('Connection to ' + str(addr))
            #sleep(1)
            log('Start ServerThread ')
            ServerThread(conn, addr).start()


#main
if __name__ == "__main__":
    sock = socket()
    #sock.settimeout(5)
    sock.bind((ADDRESS, PORT))  # адрес и порт сервиса
    sock.listen(100)  # одновременное число игроков
    log('wait for client')
    Wait(sock).start()
