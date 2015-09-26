#!/usr/bin/env python3

import ssdeep
from sys import argv
from socket import socket, AF_INET, SOCK_STREAM
from string import ascii_letters
from random import randint, shuffle
from time import sleep
from base64 import b64decode

from tinfoilhat import Checker, \
    ServiceMumbleException,     \
    ServiceCorruptException,    \
    ServiceDownException,       \
    error

letters = [
    '96:gsvpIIoXiNGyRLwwymXR7pdkqNpoA5N3XwP/kWJMS+:CXiNGyemXRx5NnwFU', # 0
    '48:rQxOthxsoGWj2K+q/5hbzRWjfI/Dzr9J3vyM7NNLXFR:htXsIjS0RMg/Dzz3Pbj', # 1
    '48:fAHUzg6eTaQddQz7acMaMfvL8MAjtwk6mJPcgloAvGu72f+hIghfj+3:fAHUzwnT6MXAMAxn5xzloWp7x9+3', # 2
    '48:tszJq2z+5JS+fzYVBSuZIanvxOYrqrImn:CzNz+5JSizYVvznvxzqUW', # 3
    '24:mdtGDm/g/FIjh6z2+fKnORZlJaNOwgA/w3J8TC74lJLweBabBNbs70BmFaK5YZbT:mmWiKniZldwc3ik4bLweBabBRimDjQ6', # 4
    '48:ek32+sCSDZfwjVZs+fKeTek0Y5SkOC6cbPFQn0nyw2ClpMI9j0K2V2IZtfwRh9A/:a+swxfKeTeXYI2SbwJb0XQ04RO', # 5
    '24:QFNePUQYPJq+qAA1nK9mMfiAZdqhm6NNfu3Vi:y8QXq3oliAPYm6Nsi', # 6
    '48:L7UBU9zJpMmPxg6ZlvsZhe9xZZxCNvVe2:cK9zjMm5VoZhefxCNN3', # 7
    '24:KBm63bQeVPNmro/vYtCbzOTQahJouS0cOl2oa/5pdA5IJio:KBm6vjmrO9bzO8ahSuvcO2xxpZJz', # 8
    '96:KmYfuS4CVzddz4g5yThbZ0itbvCR9Cse6p1/:ouBuW0NBeK', # 9
    '48:VChKz5tFO50igtzfKGGflwe2kxEhzRjTKGhTu16jOI2lBPM82jAlHUA:VChE0GGtHAh9KG5uMP2P2AJ', # a
    '48:Q4tovTRp2aVS7wHnGrpDGd2V2Zcgt+Mz0JPcjjju18iuOpaVonZqNf:ntovTRp8yGrpDW5dwJPajS8waeqf', # b
    '48:r0wowLq3+yqNb+xvRPXJOU7Pl2hXcnIU/a0tAds4d+y:/FLi+y5XJOM2hX8IatAdV+y', # c
    '48:c1RMH+dp6Qrvb1ttv2RXtgLPNt9ufMUB11wr85I10meaTJcUgT9Def0ZdkJiK:c1dp6UbFpL1t9qMUBDIu4di9TkJf', # d
    '48:wE3ZEUoKs0AB2ropu5xQO/iqfGYPe/3a9pWj/AfYrkMeUhXHjeWO+VgNK/J:wEboJ0Aw8CQFQGme/3a9pWeYQeCWOwHJ', # e
    '24:68Twqi37RfADn6YL0U76DZrhD2rv6jlmf2IxOWKlOJIbv7amFGBrHKfRkuFsxP9O:6Qi3dfA+YLvqhykm3s/bve1BrqfeuFCo', # f
]

def find_num(wavnum):
    for i, n in enumerate(letters):
        if ssdeep.compare(n, ssdeep.hash(wavnum)) > 90:
            return hex(i)[2:]

def get_wav_nums(content):
    return list(filter(lambda x: len(x) > 1000, content.split(150 * b'\xff')))

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

            sleep(0.1)
            recvd = s.recv(self.BUFSIZE)
            if recvd.find(b'NOTHING') >= 0:
                raise ServiceCorruptException()

            flag = ""
            try:
                wav = b64decode(recvd)

                flag = recognize_flag(wav)
            except:
                raise ServiceCorruptException

            return flag

        except ConnectionRefusedError:
            raise ServiceDownException()

        except ConnectionResetError:
            raise ServiceMumbleException()

        except BrokenPipeError:
            raise ServiceMumbleException()

    def chk(self, host, port):
        return True

if __name__ == '__main__':
    VoiceChecker(argv)
