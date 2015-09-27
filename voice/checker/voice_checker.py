#!/usr/bin/env python3

import ssdeep
from sys import argv, stderr
from socket import socket, AF_INET, SOCK_STREAM
from string import ascii_letters
from random import randint, shuffle
from time import sleep
from base64 import b64decode
from gzip import decompress

from tinfoilhat import Checker, \
    ServiceMumbleException,     \
    ServiceCorruptException,    \
    ServiceDownException,       \
    error

def find_num(wavnum):
    letters = [
        '96:asvpIIoXiNGyRLwwymXR7pdkqNpoA5N3XwP/kWJMS7:sXiNGyemXRx5NnwFp', # 0
        '48:bQxOthxsoGWj2K+q/5hbzRWjfI/Dzr9J3vyM7NNLXF4:RtXsIjS0RMg/Dzz3PbC', # 1
        '48:fAHUzg6eTaQddQz7acMaMfvL8MAjtwk6mJPcgloAvGu72f+hIghfj+D:fAHUzwnT6MXAMAxn5xzloWp7x9+D', # 2
        '48:mszJq2z+5JS+fzYVBSuZIanvxOYrqrImH:1zNz+5JSizYVvznvxzqU2', # 3
        '24:SdtGDm/g/FIjh6z2+fKnORZlJaNOwgA/w3J8TC74lJLweBabBNbs70BmFaK5YZbs:SmWiKniZldwc3ik4bLweBabBRimDjQv', # 4
        '48:hk32+sCSDZfwjVZs+fKeTek0Y5SkOC6cbPFQn0nyw2ClpMI9j0K2V2IZtfwRh9Ag:R+swxfKeTeXYI2SbwJb0XQ04RT', # 5
        '24:oFNePUQYPJq+qAA1nK9mMfiAZdqhm6NNfu3VV:68QXq3oliAPYm6NsV', # 6
        '48:H7UBU9zJpMmPxg6ZlvsZhe9xZZxCNvVeo:oK9zjMm5VoZhefxCNNZ', # 7
        '24:4Bm63bQeVPNmro/vYtCbzOTQahJouS0cOl2oa/5pdA5IJir:4Bm6vjmrO9bzO8ahSuvcO2xxpZJK', # 8
        '96:jmYfuS4CVzddz4g5yThbZ0itbvCR9Cse6p1s:3uBuW0NBeb', # 9
        '48:pChKz5tFO50igtzfKGGflwe2kxEhzRjTKGhTu16jOI2lBPM82jAlHUC:pChE0GGtHAh9KG5uMP2P2Az', # a
        '48:c4tovTRp2aVS7wHnGrpDGd2V2Zcgt+Mz0JPcjjju18iuOpaVonZqNg:LtovTRp8yGrpDW5dwJPajS8waeqg', # b
        '48:84tJ0wowLq3+yqNb+xvRPXJOU7Pl2hXcnIU/a0tAds4d+r:JFFLi+y5XJOM2hX8IatAdV+r', # c
        '48:B1RMH+dp6Qrvb1ttv2RXtgLPNt9ufMUB11wr85I10meaTJcUgT9Def0ZdkJiT:B1dp6UbFpL1t9qMUBDIu4di9TkJM', # d
        '48:ZE3ZEUoKs0AB2ropu5xQO/iqfGYPe/3a9pWj/AfYrkMeUhXHjeWO+VgNK/5:ZEboJ0Aw8CQFQGme/3a9pWeYQeCWOwH5', # e
        '24:58Twqi37RfADn6YL0U76DZrhD2rv6jlmf2IxOWKlOJIbv7amFGBrHKfRkuFsxP9d:5Qi3dfA+YLvqhykm3s/bve1BrqfeuFCv', # f
    ]
    for i, n in enumerate(letters):
        if ssdeep.compare(n, ssdeep.hash(wavnum)) > 90:
            return hex(i)[2:]
    return ''

def get_wav_nums(content):
    return [ a.strip(b'\xff') for a in filter(lambda x: len(x) > 1000, content.split(100 * b'\xff'))]

def recognize_flag(content):
    return ''.join([ find_num(i) for i in get_wav_nums(content)[0:40] ]) + '='


class VoiceChecker(Checker):

    BUFSIZE = 524288

    """
    Сгенерировать логин

    @return строка логина из 10 символов английского алфавита
    """
    def random_login(self):
        symbols = list(ascii_letters)
        shuffle(symbols)
        return ''.join(symbols[0:10])

    """
    Сгенерировать пароль

    @return строка пароля из 10 цифр
    """
    def random_password(self):
        return str(randint(100500**2, 100500**3))[0:10]

    """
    Положить флаг в сервис

    @param host адрес хоста
    @param port порт сервиса
    @param flag флаг
    @return состояние, необходимое для получения флага
    """
    def put(self, host, port, flag):
        try:
            s = socket(AF_INET, SOCK_STREAM)

            s.connect((host, port))

            login = self.random_login()
            password = self.random_password()

            sleep(0.1)
            if b'VOICE API\nLOGIN: ' != s.recv(self.BUFSIZE):
                error("1")
                raise ServiceMumbleException()

            s.send((login + '\n').encode('utf-8'))

            sleep(0.1)
            recvd = s.recv(self.BUFSIZE)
            if recvd.find(b'PASSWORD') < 0:
                raise ServiceMumbleException()

            s.send((password + '\n').encode('utf-8'))

            sleep(0.1)
            recvd = s.recv(self.BUFSIZE)
            if recvd.find(b'COMMAND') < 0:
                error("3" + str(recvd))
                raise ServiceMumbleException()

            s.send(b'GENERATE\n')

            sleep(0.1)
            if b'TEXT: ' != s.recv(self.BUFSIZE):
                error("4")
                raise ServiceMumbleException()

            s.send((flag.replace('=', 'equalsign') + '\n').encode('utf-8'))

            sleep(0.1)

            sleep(0.1)
            recvd = s.recv(self.BUFSIZE)
            if recvd.find(b'SUCCESS') < 0:
                error("5 " + str(recvd))
                raise ServiceMumbleException()

            return login + ":" + password

        except ConnectionRefusedError:
            raise ServiceDownException()

        except ConnectionResetError:
            raise ServiceMumbleException()

        except BrokenPipeError:
            raise ServiceMumbleException()

        except Exception as e:
            print(e, file=sys.stderr)
            raise ServiceDownException()

    """
    Получить флаг из сервиса

    @param host адрес хоста
    @param port порт сервиса
    @param state состояние
    @return флаг
    """
    def get(self, host, port, state):
        login, password = state.split(':')
        try:
            s = socket(AF_INET, SOCK_STREAM)

            s.connect((host, port))

            sleep(0.1)
            if b'VOICE API\nLOGIN: ' != s.recv(self.BUFSIZE):
                raise ServiceMumbleException()

            s.send((login + '\n').encode('utf-8'))

            sleep(0.1)
            recvd = s.recv(self.BUFSIZE)
            if recvd.find(b'PASSWORD') < 0:
                raise ServiceMumbleException()

            s.send((password + '\n').encode('utf-8'))

            sleep(0.1)
            recvd = s.recv(self.BUFSIZE)
            if recvd.find(b'COMMAND') < 0:
                raise ServiceMumbleException()

            s.send(b'DOWNLOAD\n')

            sleep(0.5)
            recvd = s.recv(self.BUFSIZE)
            if recvd.find(b'NOTHING') >= 0:
                raise ServiceCorruptException()

            flag = ""
            try:
                gzip = b64decode(recvd)

                wav = decompress(gzip)

                flag = recognize_flag(wav)
            except Exception as e:
                raise ServiceCorruptException

            return flag

        except ConnectionRefusedError:
            raise ServiceDownException()

        except ConnectionResetError:
            raise ServiceMumbleException()

        except BrokenPipeError:
            raise ServiceMumbleException()

        except Exception as e:
            print(e, file=sys.stderr)
            raise ServiceDownException()

    def chk(self, host, port):
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((host, port))
        except:
            raise ServiceDownException


if __name__ == '__main__':
    VoiceChecker(argv)
