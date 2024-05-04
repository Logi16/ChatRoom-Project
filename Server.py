import socket
from os import getcwd,mkdir, name
from os.path import exists,dirname,abspath
from csv import reader
from threading import Thread
from datetime import datetime
from random import randrange
from traceback import print_exc
import traceback

clientList={}

class Colour(Exception):
    pass

class user():
    def __init__(self,name,connection,address,colour):
        self._name=name
        self._conn=connection
        self.__addr=address
        self._colour=colour

    @property
    def name(self):
        '''Name Getter'''
        return self._name

    @property
    def conn(self):
        '''Connection Getter'''
        return self._conn

    @property
    def col(self):
        '''Colour Getter'''
        return self._colour

    def __str__(self):
        return f"@{self._name},{self._colour}"

class Server():
    def __init__(self):
        self.SERVER=socket.gethostbyname(socket.gethostname()) 
        #self.SERVER='localhost'
        self.PORT=5050
        self.HEADER=64
        self.PATH=dirname(abspath(__file__))
        self.LOGS="{}/{}.txt".format(self.PATH+"\Logs",datetime.now().strftime('%Y-%m-%d'))
        if not exists(self.PATH+"\Logs"):
            mkdir(self.PATH+"\Logs")
        with open(self.PATH+"\\tk-colours.csv","r") as f:
            self.COLOURS=[]
            for i in reader(f):
                self.COLOURS.append(i[1])
        self.CLIENTLIST={}

    @staticmethod
    def Broadcast(clientList,msg):
        #Sends message to everyone in client list
        if not clientList:
            pass
        else:
            for i in list(clientList.keys()):
                Server.Send(msg,clientList[i].conn)
        with open(Server.LOGS,'a') as f:
            f.write(msg+"\n")

    @staticmethod
    def Send(msg,conn):
        bMsg=msg.encode()
        msgLength=str(len(bMsg)).encode()
        msgLength+=b' '*(Server.HEADER-len(msgLength))
        #print(msgLength)
        conn.send(msgLength)
        #print(bMsg)
        conn.send(bMsg)

    @staticmethod
    def Joining(clientList,conn,addr):
        #Receiving username
        amount=int(conn.recv(Server.HEADER))
        username=conn.recv(amount).decode().strip()
        if not clientList:
            Server.Send("Accepted",conn)
        else:
            for i in list(clientList.keys()):
                if i.lower()==username.lower():
                    Server.Send("Username Taken",conn)
                    conn.close()
                    return
            Server.Send("Accepted",conn)
        validCol=False
        while validCol==False:
            try:
                colour=Server.COLOURS[randrange(0,len(Server.COLOURS))]
                if not clientList:
                    validCol=True
                    pass
                else:
                    for i in list(clientList.keys()):
                        if clientList[i].col == colour:
                            raise Colour
                        else:
                            pass
                    validCol=True
            except Colour:
                pass
            except:
                print_exc()
        Server.Send(colour,conn)
        person=user(username,conn,addr,colour)
        for i in clientList.keys():
            print(str(clientList[i]))
            Server.Send(str(clientList[i]),conn)
        clientList[username]=person
        Server.Broadcast(clientList,str(person))
        welcome="{}|[{}] [+] {} has joined.".format("#32CD32",datetime.now().strftime('%Y-%m-%d %H:%M:%S'),username)
        print(welcome)
        Server.Broadcast(clientList,welcome)
        Server.Recieving(clientList,person)

    @staticmethod
    def Recieving(clientList,client):
        try:
            while True:
                amount=int(client.conn.recv(Server.HEADER).decode())
                msg=client.conn.recv(amount).decode()
                msg = "{}|[{}] {}: {}".format(client.col,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),client.name,msg)
                #Sending to all clients
                Server.Broadcast(clientList,msg)
        except:
            traceback.print_exc()
            clientList.pop(client.name)
            leave="{}|[{}] [-] {} has left.".format("#32CD32",datetime.now().strftime('%Y-%m-%d %H:%M:%S'),client.name)
            print(leave)
            Server.Broadcast(clientList,leave)

    @staticmethod
    def Main():
        Server.__init__(Server)
        #Creating socket with correct settings
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((Server.SERVER, Server.PORT))
        #Start and announce listening
        s.listen()
        print(f"[*] Listening on {Server.SERVER} with port {Server.PORT} as {socket.gethostname()}")
        while True:
            #Always listening
            connection,address=s.accept()
            print("Connected")
            #Doing threading
            t = Thread(target=Server.Joining,daemon=True,args=(Server.CLIENTLIST,connection,address))
            t.start()

if __name__ == '__main__':
    Server.Main()