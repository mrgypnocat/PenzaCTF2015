# -*- coding: utf-8 -*-
#!/usr/bin/python3

from sys import stderr

from socket import socket
from time import strftime, sleep
from collections import namedtuple
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import random
import pickle

STATUS_CHECKER_ERROR = 1
STATUS_SERVICE_MUMBLE = 2
STATUS_SERVICE_CORRUPT = 3
STATUS_SERVICE_DOWN = 4

Command = namedtuple("Command",
    "command user pub_key priv_key data_id data signature")


class ServiceMumbleException(Exception):
    pass


class ServiceCorruptException(Exception):
    pass


class ServiceDownException(Exception):
    pass


class NonImplementedException(Exception):
    pass



def Auth(conn):
    #ключ чекера
    try:
        f = open("MainKey2", 'rb')
        key = RSA.importKey(f.read())
    except:
        return -1

    data = conn.recv(2048)

    hash = SHA256.new()
    hash.update(data)
    h = hash.digest()

    conn.sendall(key.encrypt(h, "")[0])
    return 0

def error(s):
    print(s, file=stderr)


class Checker(object):

    def usage(self):
        error("Usage:")
        error("\tput HOST PORT FLAG\tПоложить флаг в сервис. Возвращает состояние.")
        error("\tget HOST PORT STATE\tПолучить флаг из сервиса для состояния.")
        error("\tchk HOST PORT\tПроверить доступность и целостность сервиса.")

    def __init__(self, argv):
        if len(argv) < 3:
            self.usage()
            exit(STATUS_CHECKER_ERROR)

        try:
            error(argv)
            cmd = argv[1]
            host = argv[2]
            port = int(argv[3])

            if "put" == cmd:
                if len(argv) < 5:
                    error("Недостаточно аргументов.")
                    exit(STATUS_CHECKER_ERROR)
                flag = argv[4]
                error('Put flag \'' + str(flag) + '\' to '
                      + str(host) + ':' + str(port))
                print(self.put(host, port, flag))

            elif "get" == cmd:
                if len(argv) < 5:
                    error("Недостаточно аргументов.")
                    exit(STATUS_CHECKER_ERROR)
                state = argv[4]
                error('Get flag from ' + str(host) + ':' + str(port))
                print(self.get(host, port, state))

            elif "chk" == cmd:
                error('Check status of ' + str(host) + ':' + str(port))
                self.chk(host, port)

            else:
                self.usage()
                exit(STATUS_CHECKER_ERROR)

        except ServiceMumbleException:
            exit(STATUS_SERVICE_MUMBLE)

        except ServiceCorruptException:
            exit(STATUS_SERVICE_CORRUPT)

        except ServiceDownException:
            exit(STATUS_SERVICE_DOWN)


    """
    Положить флаг в сервис

    @param host адрес хоста
    @param port порт сервиса
    @param flag флаг
    @return состояние, необходимое для получения флага
    """
    def put(self, host, port, flag):

        sock = socket()
        try:
            sock.connect((host, port))
        except:
            raise ServiceDownException()


        message1 = Command(command='putf',
                    user='',
                    signature='',
                    data=flag,
                    pub_key="",
                    priv_key="",
                    data_id="")
        dmp = pickle.dumps(message1)
        try:
            sock.sendall(dmp)
        except:
            raise ServiceMumbleException()

        if(Auth(sock)):
            raise ServiceMumbleException()

        try:
            data = str(sock.recv(1024)).replace("b'", "").replace("'", "")
        except:
            raise ServiceMumbleException()

        if(data=="OK"):
            return
        elif(data=="MUMBLE"):
            raise ServiceMumbleException()
        elif(data=="DOWN"):
            raise ServiceDownException()
        else:
            raise ServiceMumbleException()


    """
    Получить флаг из сервиса

    @param host адрес хоста
    @param port порт сервиса
    @param state состояние
    @return флаг
    """
    def get(self, host, port, state):
        sock = socket()
        try:
            sock.connect((host, port))
        except:
            raise ServiceDownException()


        message1 = Command(command='getf',
                    user='',
                    signature='',
                    data='',
                    pub_key="",
                    priv_key="",
                    data_id="")
        dmp = pickle.dumps(message1)
        try:
            sock.sendall(dmp)
        except:
            raise ServiceMumbleException()

        if(Auth(sock)):
            raise ServiceMumbleException()

        try:
            data = str(sock.recv(1024)).replace("b'", "").replace("'", "")
        except:
            raise ServiceMumbleException()

        if(data=="MUMBLE"):
            raise ServiceMumbleException()
        elif(data=="DOWN"):
            raise ServiceDownException()
        else:
            raise ServiceMumbleException()

        return data


    """
    Проверить состояние сервиса

    @param host адрес хоста
    @param port порт сервиса
    """
    def chk(self, host, port):
        self.get(host, port, "")


if __name__ == '__main__':

    error("Interactive run not supported")