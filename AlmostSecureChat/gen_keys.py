# -*- coding: utf-8 -*-
#!/usr/bin/env python3

#imports
from Crypto.PublicKey import RSA
from Crypto import Random


random_generator = Random.new().read
key = RSA.generate(1024, random_generator)

user_pub_key = key.publickey().exportKey("PEM")
user_private_key = key.exportKey("PEM")


f = open("pubkey", 'wb')
f.write(user_pub_key)
f.close()

z = open("pprivkey", 'wb')
z.write(user_private_key)
z.close()

