import socket
from time import strftime, sleep
from threading import Thread, current_thread
import re
from sys import version

RCV_PORT = 33333
IP_ADDRESS = '127.0.0.1'

class ListenerThread(Thread):

    def __init__(self, conn, addr):

            Thread.__init__(self)
            self.conn = conn
            self.addr = addr

   
    def user_interaction(self, conn, addr):

        self.conn.sendall('This is alpha demo calculator.\n'.encode('utf-8'))
        self.conn.sendall('Enter your evaluation: \n'.encode('utf-8'))
        while True:
            data = self.conn.recv(1024)
            if not data:
                log('no data from ' + str(self.addr))
                return
            break
            log('got data ' + str(data) + ' from ' + str(self.addr))

          
    def run(self):

        try:
            log('Started GameThread with ' + str(self.addr))
            self.user_interaction(self.conn, self.addr)
        except Exception as e:
            log("ending play with error: " + str(e) + ' to ' + str(self.addr))
        finally:
            log('ending play with ' + str(self.addr))
            self.conn.close()

class Wait(Thread):

    def __init__(self, sock):
        Thread.__init__(self)
        self.game_sock = sock

    def run(self):
        while (True):
            conn, addr = self.game_sock.accept()
            log('Connection to ' + str(addr))
            sleep(1)
            log('Start GameThread ')
            GameThread(conn, addr).start()