# -*- coding: utf-8 -*-
#!/usr/bin/env python3

#imports
from socket import socket
from peewee import *
from threading import Thread
from collections import namedtuple
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import random
import binascii
import pickle

#globals
PORT = 33334
SPORT = 33333
ADDRESS = '127.0.0.1'

Command = namedtuple("Command",
	"command user pub_key priv_key data_id data signature")


class ServiceMumbleException(Exception):
	pass


class ServiceCorruptException(Exception):
	pass


class ServiceDownException(Exception):
	pass


class User:

	def __init__(self, key, IP):
		self.IP = IP
		self.pubkey = key


def SCommand(cmd):

	#подключиться к серверу
	try:
		f = open("FlagerKey", 'rb')
		key = RSA.importKey(f.read())
		uname = "checker"
	except Exception as e:
		print("You must register user 'checker' on server " + \
			"and place it's keyfile with name 'checker_key'")
		return -1

	sock = socket()
	try:
		sock.connect((ADDRESS, SPORT))
	except Exception as e:
		print ('Connection to server fails')
		return -2
	
	
	print ('sconnect')
	# messages
	sock.recv(1024)
	sock.recv(1024)

	cmd = str(cmd).replace("b'", "").replace("'", "")

	print(cmd)

	if (cmd.split()[0] == 'select'):
		hash = SHA256.new()
		hs = cmd.split()[0] + uname + cmd.split()[1]
		hash.update(hs.encode("utf-8"))
		hash_string = hash.digest()
		emsg = str(binascii.hexlify(key.encrypt(hash_string, "")[0]))
		sock.sendall((cmd.split()[0] + ' ' + uname + ' ' + cmd.split()[1] + ' '
			+ emsg).encode('utf-8'))

		data = sock.recv(2048)

		if not data:
			print('No reply from server')
			return -1
		else:
			return data

	elif (cmd.split()[0] == 'insert'):
		hash = SHA256.new()
		hs = cmd.split()[0] + uname + cmd.split()[1] + cmd.split()[2]
		hash.update(hs.encode("utf-8"))
		hash_string = hash.digest()
		emsg = str(binascii.hexlify(key.encrypt(hash_string, "")[0]))

		sock.sendall((cmd.split()[0] + ' ' + uname + ' ' + cmd.split()[1] +
				' ' + cmd.split()[2] + ' ' + emsg).encode('utf-8'))

		data = sock.recv(2048)
		if not data:
			print('No reply from server')
			return -1
		return 0

	elif (cmd.split()[0] == 'get'):
		sock.sendall(cmd.encode('utf-8'))
		data = sock.recv(2048)

		reply = str(data).replace("b'", '').replace("'", "") \
			.replace("\\n", "\n").replace('"', "").split("\n")

		pk = reply[0] + '\n' + reply[1] + '\n' + reply[2] + '\n' + reply[3] \
				+ '\n' + reply[4] + '\n' + reply[5] + reply[6] + '\n' + \
				reply[7] + '\n' + reply[8] + '\n' + reply[9] + '\n' + reply[10] \
				+ '\n' + reply[11] + '\n' + reply[12] + '\n'+reply[13] + '\n' + \
				reply[14]
		ipc = reply[15]

		data_str = str(data).replace("b'", '').replace("'", "")
		if data:
			return User(pk, ipc)
		else:
			print('No reply from server')
			return -1
		return 0

	else:
		print ('Wtf you sent me you moron')
		return -1


def AuthChk(conn):
	#ключ чекера
	try:
		f = open("MainKey", 'rb')
		key = RSA.importKey(f.read())
	except Exception as e:
		print(e)
		return -1

	random.seed()
	r = str(random.getrandbits(128))

	hash = SHA256.new()
	hash.update(r.encode('utf-8'))
	h = hash.digest()

	conn.sendall(r.encode('utf-8'))
	t = conn.recv(2048)
		
	if (key.decrypt(t) != h):
		return -1
		
	
	return 0


class ServerThread(Thread):

	def __init__(self, conn, addr):

		Thread.__init__(self)
		self.conn = conn
		self.addr = addr

	# взаимодействие с клиентом
	def user_interaction(self, conn, addr):
		print("UI started")
		try:
			f = open("FlagerKey", 'rb')
			key = RSA.importKey(f.read())
			uname = "checker"
		except:
			print("You must register user 'checker' on server " + \
				"and place it's keyfile with name 'checker_key'")
			raise ServiceMumbleException()

		try:

			while True:
				msg = self.conn.recv(8192)  # максимальный размер сообщения
				if not msg:
					return
				break

			message = pickle.loads(msg)
			print(message.command)

			if (message.command == 'auth'):
				print("Got auth")

				hash = SHA256.new()
				hash.update(message.command.encode('utf-8'))
				hash.update(message.user.encode('utf-8'))
				hash.update(message.data.encode('utf-8'))
				h = hash.digest()

				#получить ключ от сервера
				print("Try to get key")
				pk = SCommand(('get ' + message.user).encode('utf-8')).pubkey

				print("Got key")
				Other_key = RSA.importKey(pk)

				if (h != Other_key.decrypt(message.signature)):
					print('Verification failed')
					return

				print("Verification passed")
				hash = SHA256.new()
				hash.update(message.data.encode('utf-8'))
				h = hash.digest()

				message1 = Command(command='auth_done',
					user='',
					signature=key.encrypt(h, ""),
					data="",
					pub_key="",
					priv_key="",
					data_id="")
				dmp = pickle.dumps(message1)
				conn.sendall(dmp)

				print("Chat ready")
				conn.settimeout(5)
				conn.recv(1024)
				conn.sendall("No chat for you here")
				conn.close()

			elif (message.command == 'putf'):

				a = AuthChk(conn)
				
				if(a==-2):
					conn.sendall("DOWN".encode('utf-8'))
				else:
					if(not a):
						try:
							res = SCommand('insert ' + str(message.data) + ' 1')
							if (not res):
								conn.sendall("OK".encode('utf-8'))
							else:
								conn.sendall("MUMBLE".encode('utf-8'))
						except Exception as e:
							print (e)
							conn.sendall("MUMBLE".encode('utf-8'))
					else:
						conn.sendall("AuthErr".encode('utf-8'))

			elif (message.command == 'getf'):

				a = AuthChk(conn)
				if(a==-2):
					conn.sendall("DOWN".encode('utf-8'))
				else:
					if(not a):
						try:
							flag = SCommand('select 1')
							conn.sendall(flag)
						except Exception as e:
							print (e)
							conn.sendall("MUMBLE".encode('utf-8'))
					else:
						conn.sendall("AuthErr".encode('utf-8'))

			else:
				conn.sendall("Lolwat".encode('utf-8'))

		except Exception as e:
			print(e)
			return

	def run(self):

		try:
			self.user_interaction(self.conn, self.addr)
		except:
			pass
		self.conn.close()


class Wait(Thread):

	def __init__(self, sock):
		Thread.__init__(self)
		self.game_sock = sock

	def run(self):
		while (True):
			conn, addr = self.game_sock.accept()
			ServerThread(conn, addr).start()


#main
if __name__ == "__main__":
	sock = socket()
	sock.bind((ADDRESS, PORT))  # адрес и порт шняги
	sock.listen(100)  # одновременное число игроков
	Wait(sock).start()
