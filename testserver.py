import socket
import threading
import time
import os
from scapy.all import *
import random


devserver = get_if_addr('eth1')
testserver = get_if_addr('eth2')
#SERVER = socket.gethostbyname("172.18.0.8") # Should be 172.l.0.14 - Our hostname
SERVER = testserver
BROADCAST_PORT = 13117
SERVER_PORT = 2008 #ours
ADDR = (SERVER,SERVER_PORT) 
FORMAT = 'utf-8'

flag = True
flag2 = True


#The UDP Connections:
broadcastServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
broadcastServer.bind(ADDR) # new i added
# Enable broadcasting mode
broadcastServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcastServer.settimeout(0.2)

#The TCP Connections:
TCPserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCPserver.bind(ADDR)

#For game
whowon = {}

#SET SCREEN:
os.system("cls")
COLORS = {'Black': '\u001b[30m', \
'Red': '\u001b[31m' ,\
'Green': '\u001b[32m',\
'Yellow': '\u001b[33m',\
'Blue': '\u001b[34m',\
'Magenta': '\u001b[35m',\
'Cyan': '\u001b[36m',\
'White': '\u001b[37m',\
'Reset': '\u001b[0m'}





def broadcast_message_before_game():
    global flag 
    header = bytes.fromhex('abcddcba') + bytes.fromhex('02') + bytes.fromhex('07D8')
    broadcast_message = header
    while(flag):
        broadcastServer.sendto(broadcast_message, ('<broadcast>', 13117))
        time.sleep(1) 
    
    



def listen(Connections,Clients):
    global flag
    while(flag):
        if(len(Connections) == 1 or len(Clients) == 1):
            startTime = time.time()
            TCPserver.listen()
            conn, addr = TCPserver.accept()
            data = conn.recv(1024)
            playerName = data.decode(FORMAT).split('\n')[0]
            Connections[playerName] = conn
            Clients[playerName] = addr[0] 
            print("2 users connected, waiting 10 seconds till we start the game")
            time.sleep(10)            
            flag = False
        elif(len(Connections) == 0 or len(Clients) == 0):
            TCPserver.listen()
            conn, addr = TCPserver.accept()
            data = conn.recv(1024)
            playerName = data.decode(FORMAT).split('\n')[0]
            Connections[playerName] = conn
            Clients[playerName] = addr[0] 



    
        
    

def start():
    print (f"Server started, listening on IP address {SERVER}")
    
    while True:            
        try:
            global flag
            global flag2
            flag = True
            flag2 = True
            Clients = {} # {Name: ip}
            Connections = {} #{name : connection per game}
            
            thread = threading.Thread(target=listen,args = (Connections,Clients)) #thread per tcp start connection
            thread2 = threading.Thread(target=broadcast_message_before_game) #thread per broadcasts
            thread.start()
            thread2.start()
            thread.join()
            thread2.join()
            print(Connections)
            print(Clients)
        except Exception as e:
            print("connection lost")
            continue


        #Enter the game:
        if(len(Clients.keys()) > 0):
                    
             # building the welcome message
            message = '*******************************************\n'
            message += 'Welcome to Quick Maths.\n'
            i=1
            for p in Clients.keys():
                message +='Player '+str(i)+': '+p+'\n'
                i+=1
            message += '==\nPlease answer the following question as fast as you can:\n'
            equationresult,equationstring = choose_equation()
            message += 'How much is ' + equationstring + '?\n'
            print(message)
            for name in Connections.keys():
                whowon[name] = False
            for name in Connections.keys():
                 #Get any user connection:
                
                conn_player = Connections[name]
                conn_player.settimeout(30) #After that the server move on - raise a time out exception
                
                #thread per user:
                thread_game = threading.Thread(target=game,args=(name,conn_player,message,equationresult))
                thread_game.start()
                #maybe switch to thread_game.join()
                while(flag2 == True):
                    time.sleep(0.1)
            print(COLORS['Green'] + "Game Over!\n")
            print(COLORS['Green'] + "The correct answer was " + str(equationresult) +"\n")
            print('\n')
            counteri = 0
            for name,won in whowon.items():
                if(won == True):
                    counteri+=1
                    print(COLORS['Green'] + "Congratulations to the winner: " + name + "\n")
            if(counteri == 0):
                print(COLORS['Red']+"Times up!\n")
                print(COLORS['Red']+"No one has answered correctly in 10 seconds so we have a draw!\n")
            #Send the end message:
            for name in Connections.keys():
                conn_player = Connections[name]
                if(whowon[name] == True):
                    endgamemessage = "You have won, Congratulations"
                thread_endgame = threading.Thread(target=endgame,args=(name,conn_player,endgamemessage))
                thread_endgame.start()
                thread.join(1)
            print(COLORS["Reset"]+"Game over, sending out offer requests...")
        else:
            print(COLORS["Reset"]+"No game, sending out offer requests...")    
                

def game(name,conn_player,messageStart,equationresult):
    try:
        global flag2
        #Start Game Message:
        conn_player.send(messageStart.encode(FORMAT))
        conn_player.send(str(equationresult).encode(FORMAT))

        start_game_time = time.time()
        while(start_game_time + 10 > time.time()):
            data,addr = conn_player.recvfrom(1024)
            while(flag2 == True):
                key = data.decode(FORMAT)
                if(key.isnumeric()):
                    if(int(key) == equationresult):       
                        flag2 = False
                        whowon[name] = True
                    else:
                        break         
    except:
        pass

def choose_equation():
    possible_equations = [(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,0),(0,1)
    ,(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(2,7),(2,0),(0,2)
    ,(3,1),(3,2),(3,3),(3,4),(3,5),(3,6),(3,0),(0,3)
    ,(4,1),(4,2),(4,3),(4,4),(4,5),(4,0),(0,4)
    ,(5,1),(5,2),(5,3),(5,4),(5,0),(0,5)
    ,(6,1),(6,2),(6,3),(6,0),(0,6)
    ,(7,1),(7,2),(7,0),(0,7)
    ,(8,1),(8,0),(0,8)
    ,(9,0),(0,9)]
    randomnum = random.randint(0,53)
    equationdue = possible_equations[randomnum]
    equationresult = equationdue[0] + equationdue[1]
    equationstring = str(equationdue[0]) + "+" + str(equationdue[1])
    return equationresult,equationstring

        
def endgame(name, conn_player, endgamemessage):
    try:
        conn_player.send(endgamemessage.encode(FORMAT))
        print (f"Connection with {name} close")
        conn_player.close()
    except:
        pass
    
    
start()


