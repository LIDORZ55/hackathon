import os
import time
import socket
import threading
import getch
import sys
import select
from time import sleep
import multiprocessing
import struct

#Default:
PORT = 0
SERVER_ADDR = 0
FORMAT = 'utf-8'

SERVER = socket.gethostbyname(socket.gethostname()) 
ADDR = (SERVER,PORT)

#global param
flag = True

#SET SCREEN:
os.system("clear")
COLORS = {'Black': '\u001b[30m', \
'Red': '\u001b[31m' ,\
'Green': '\u001b[32m',\
'Yellow': '\u001b[33m',\
'Blue': '\u001b[34m',\
'Magenta': '\u001b[35m',\
'Cyan': '\u001b[36m',\
'White': '\u001b[37m',\
'Reset': '\u001b[0m'}

clientUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP


# Enable broadcasting mode
clientUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
clientUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
clientUDP.bind(("", 13117))




def start():
    while True:
        global flag 
        flag = True
        #Broadcast:
        print("Client started, listening for offer requests... ")
        data, addr = clientUDP.recvfrom(1024)
        (magicCookie, msg_type, server_port) = struct.unpack('!IbH', data)
        #Check the message format:
        #if magicCookie == 0xabcddcba:
        #    if msg_type == 0x2:

        #header = data[:5]
        ##print(addr[0])
        address = addr[0]
        
        #Check the message format:
        #if header == bytes.fromhex('abcddcba') + bytes.fromhex('02'):
        if magicCookie == 0xabcddcba and msg_type == 0x2:

            #dest_port = int.from_bytes(data[5:7],"big")
            #print("the address in which the udp broadcast came from: " + address)
            #print(dest_port)
            SERVER_ADDR = (address,server_port)
            
            print(f"Received offer from {address} , attempting to connect...")
            
            #Enable TCP connection:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print(1)
            client.connect(SERVER_ADDR)
            #print(2)
            fromuser = sys.argv[1] + "\n" #
            #print(3)
            client.send(fromuser.encode(FORMAT))
            #print(4)
            
            #Game starts:
            data, addr = client.recvfrom(100000)
            print(COLORS["Blue"] + data.decode(FORMAT))
            data, addr = client.recvfrom(100000)
            equationresult1 = data.decode(FORMAT)
            equationresult = int(float(equationresult1))



            def game():
                global flag
                start_game_time = time.time()
                while(start_game_time + 10 > time.time() and flag == True):
                    try:
                        key = getch.getch()
                        client.send(key.encode(FORMAT))
                        if(key.isnumeric()):
                            if(int(float(key)) == equationresult):       
                                flag = False
                        sleep(0.5)
                    except Exception as e:
                        print (e)
                        pass         
            
            try:
                proc = multiprocessing.Process(target=game, args=())
                proc.start()
                data, addr = client.recvfrom(100000)
                if(data.decode(FORMAT) == "You have lost, better luck next time"):
                    proc.terminate()
                    print(COLORS["Blue"]+data.decode(FORMAT))
                if(data.decode(FORMAT) == "You have won, Congratulations"):
                    print(COLORS["Blue"]+data.decode(FORMAT))
                #Times up!
                #if(flag == True):
                #    print(COLORS["Red"]+"Time's Up!")     
            except Exception as e:
                print(e)
                pass
            client = None
            print(COLORS["Reset"]+"Server disconnected, listening for offer requests...")
            sleep(1)
            #EndGame:
            #if(flag != True):
            #    data,addr = client.recvfrom(10000)              
            
    

start()
