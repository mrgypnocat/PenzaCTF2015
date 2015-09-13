#!/usr/bin/env python3

import socket
from time import strftime, sleep
from threading import Thread, current_thread
import re
from sys import version
import json


from ConnecionsHandler import ListenerThread


if __name__ == '__main__':

    
    # Create handler thread
    LT = ListenerThread()
    
    # Read server's public key

    # Trying to read registration file


    Registred = False

    if Registred:        # Start handler thread
        LT.start()
        
    else:                   
        # Otherwise, start the UI and wait for registration

        # Create socket
        sock = socket.socket()
        sock.bind((IP_ADDRESS, SEND_PORT)) 

        #
        # Show registration form
    