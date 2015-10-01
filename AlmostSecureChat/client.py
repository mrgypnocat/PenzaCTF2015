# -*- coding: utf-8 -*-
#!/usr/bin/env python3

#imports
from socket import socket
from time import strftime, sleep
from threading import Thread, current_thread
from collections import namedtuple
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import binascii

import random
import pickle
import re

#globals
PORT = 33333
СPORT = 33334
ADDRESS = '127.0.0.1'

Command = namedtuple("Command", "command user pub_key priv_key data_id data signature")


#functions
class User:
	def __init__(self, key, IP):
		self.IP = IP
		self.pubkey = key
	

def SConnect(serverIP):

	pr_key_file = input('Set keyfile for server, if it exists ')
	
	
	try:
		f = open(pr_key_file,'rb')
		key = RSA.importKey(f.read())
		key_present = 1
		uname = input('Set username for key: ')
	except:
		key_present = 0
		
	
	UserBase = dict()

	
	# messages
	
	while(1):
		sock = socket()
		try:
			sock.connect( (serverIP, PORT) )
		except:
			print ('Connection to server fails')
			return
		
		sock.recv(1024)
		sock.recv(1024)
		
		if(not key_present):
			uname = input('Type desired name for server\n')
			sock.sendall(('register ' + uname).encode('utf-8'))
			reply = sock.recv(2048)
			
			if not reply:
				return
			
			reply = str(reply).replace("b'", '').replace("'", "").replace("\\\\n", "\n").replace('"', "").split(' ')
			
			pubkey_str = reply[7]+' '+reply[8]+' '+reply[9]+' '+reply[10]+' '+reply[11]
			privkey_str = reply[15]+' '+reply[16]+' '+reply[17]+' '+reply[18]+' '+reply[19]+' '+reply[20]+' '+reply[21]
			
			key = RSA.importKey(pubkey_str)
			f = open("KeyFile" + uname,'wb')
			f.write(pubkey_str.encode('utf-8'))
			key_present = 1

			
			
		cmd = input('select <data_id>: get data with data_id\n' + \
			'insert <data> <data_id>: save data with data_id\n'+\
			'get <username> : get IP and pubkey for username\n'+\
			'connect <username>: connect to listener client\n'+\
			'listen: wait for connection from other client\n')
			
		while (not cmd):
			cmd = input('select <data_id>: get data with data_id\n' + \
			'insert <data_id> <data>: save data with data_id\n'+\
			'get <username> : get IP and pubkey for username\n'+\
			'connect <username>: connect to listener client\n'+\
			'listen: wait for connection from other client\n')
			
			
		if (cmd.split()[0]=='select'):		
			hash = SHA256.new()
			hs = cmd.split()[0]+uname+ cmd.split()[1]
			hash.update(hs.encode("utf-8"))
			hash_string = hash.digest()
			emsg = str(binascii.hexlify(key.encrypt(hash_string, "")[0]))
		
			sock.sendall((cmd.split()[0]+' '+uname+ ' '+cmd.split()[1]+\
			' '+emsg).encode('utf-8'))
			
			data = sock.recv(2048)
			
			if(data):
				print('Recieved: ' + str(data))
			else:
				print('No reply from server')
				return
				
		elif(cmd.split()[0]=='insert'):
			hash = SHA256.new()
			hs = cmd.split()[0]+uname+ cmd.split()[1]+cmd.split()[2]
			hash.update(hs.encode("utf-8"))
			hash_string = hash.digest()
			emsg = str(binascii.hexlify(key.encrypt(hash_string, "")[0]))
		
			sock.sendall((cmd.split()[0]+' '+uname+ ' '+cmd.split()[1]+\
			' '+cmd.split()[2]+' ' +emsg).encode('utf-8'))
			
			data = sock.recv(2048)
			if(data):
				print(data)
			else:
				print('No reply from server')
				return
				
		elif(cmd.split()[0]=='get'):
			sock.sendall(cmd.encode('utf-8'))
			data = sock.recv(2048)
			
			reply = str(data).replace("b'", '').replace("'", "").replace("\\n", "\n").replace('"', "").split("\n")
														
			pk = reply[0]+'\n'+reply[1]+'\n'+reply[2]+'\n'+reply[3]+'\n'+reply[4]+'\n'+reply[5]+\
				reply[6]+'\n'+reply[7]+'\n'+reply[8]+'\n'+reply[9]+'\n'+reply[10]+'\n'+reply[11]+\
				'\n'+reply[12]+'\n'+reply[13]+'\n'+reply[14]
			ipc= reply[15]
									
			
			data_str = str(data).replace("b'", '').replace("'", "")
			if(data):
				print('User ' + cmd.split()[1] + ' has pubkey ' +\
				pk + '\nand IP ' + ipc)
				UserBase[cmd.split()[1]] = User(pk, ipc)
			else:
				print('No reply from server')
				return
			
		elif(cmd.split()[0]=='connect'):
			if(data):
				if cmd.split()[1] in UserBase:
					CConnect(uname, key, cmd.split()[1], UserBase[cmd.split()[1]])
				else:
					print('No info for user. Try to get it from server')					
			else:
				print('No reply from server')
				return
			
		elif (cmd.split()[0]=='listen'):
			CListen(sock, key)      
		
		else:
			print('Wrong command')	
			
			
def CListen(server_socket, key):
	Csock = socket()
	Csock.bind((ADDRESS, СPORT))  # адрес и порт клиента
	Csock.listen(1)  # одновременное число подключившихся
	Csock.settimeout(60)
	
	conn, addr = Csock.accept()
	print('Connected by', addr)
	
	try:
		msg = conn.recv(4096)
		
		message = pickle.loads(msg)
		if(message.command != 'auth'):
			print ('Protocol error')
			return
			
		hash = SHA256.new()
		hash.update(message.command.encode('utf-8'))
		hash.update(message.user.encode('utf-8'))
		hash.update(message.data.encode('utf-8'))
		h=hash.digest()
			
					
			#получить ключ от сервера
		server_socket.sendall(('get ' + message.user).encode('utf-8'))
		other_data = server_socket.recv(2048)
			
		reply = str(other_data).replace("b'", '').replace("'", "").replace("\\n", "\n").replace('"', "").split("\n")
					
		pk = reply[0]+'\n'+reply[1]+'\n'+reply[2]+'\n'+reply[3]+'\n'+reply[4]+'\n'+reply[5]+\
						reply[6]+'\n'+reply[7]+'\n'+reply[8]+'\n'+reply[9]+'\n'+reply[10]+'\n'+reply[11]+\
						'\n'+reply[12]+'\n'+reply[13]+'\n'+reply[14]

		
		Other_key = RSA.importKey(pk)
		
		
			
		if (h != Other_key.decrypt(message.signature)):
			print('Verification failed')
			return
		
		
		hash = SHA256.new()
		hash.update(message.data.encode('utf-8'))
		h=hash.digest()

		message1 = Command(command= 'auth_done', user = '', signature = key.encrypt(h, ""), data="", pub_key="", priv_key="", data_id="")
		dmp = pickle.dumps(message1)
		conn.sendall(dmp)
		
		print('Chat is ready')
		print('quit to quit')
				
		while True:
			data = conn.recv(1024)
			if not data: break
			print(str(data))
			str1 = input('\n> ').encode('utf-8')
			if str1=="quit":
				break
			conn.sendall(str1)
			
		conn.close()
	except:
		print('Closing connection')
	

def CConnect(name, key, client_name, client_info):
	Csock = socket()
		
	try:
		Csock.connect( (client_info.IP, СPORT) ) 
			
		print ('Connected')
			
		random.seed()		
		r = str(random.getrandbits(128))
			
		hash = SHA256.new()
		hash.update('auth'.encode('utf-8'))
		hash.update(name.encode('utf-8'))
		hash.update(r.encode('utf-8'))
		h=hash.digest()
		
			
		msg = Command(command="auth", user=name, pub_key="", priv_key="", data_id="", data=r, signature=key.encrypt(h, ""))
		dmp = pickle.dumps(msg)
		Csock.sendall(dmp)
			
		print('Request sended')	
		
			
		message = Csock.recv(8192)
		msg1 = pickle.loads(message)
			
		hash = SHA256.new()
		hash.update(r.encode('utf-8'))
		h=hash.digest()
		
		Other_key = RSA.importKey(client_info.pubkey)
		
		if(msg1.command!='auth_done' or Other_key.decrypt(msg1.signature)!=h):
			print('Verification failed')
			return
			
		print("Chat is ready")
		print("quit to quit")
			
		while True:
			str2 = input('\n> ').encode('utf-8')
			if str2=="quit":
				break
			Csock.sendall(str2)
			data = Csock.recv(1024)
			if not data: break
			print(str(data))
				
			
			
	except:
		print('Closing connection\n')
	
	
	
	
#main
if __name__ == "__main__":
    

    while(1):
        serverIP = input('Set Server\'s IP\n')
        SConnect(serverIP)        
