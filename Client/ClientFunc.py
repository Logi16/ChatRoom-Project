from socket import socket
from traceback import print_exc

def socketConnect(username,ip):
    '''Connects to sockets and asks if username is taken'''
    try:
        sock=socket()
        sock.connect((ip,5050))
        colour=sendUsername(sock,username)
        if colour == False:
            return "Taken"
        else:
            return (sock,colour)
    except:
        #print_exc()
        return False

def sendUsername(sock,username):
    '''Sends username and gives response, if accepted gives colour too'''
    try:
        send(username,sock)
        amount=int(sock.recv(64).decode())
        #print(amount)
        response=sock.recv(amount).decode()
        #print(response)
        if response == "Username Taken":
            sock.close()
            return False
        else:
            try:
                amount2=int(sock.recv(64).decode())
            except:
                print_exc()
            #print(amount2)
            colour=str(sock.recv(amount2).decode())
            #print(colour)
            return colour
    except:
        print_exc()

def send(msg,conn):
    '''Sends the length of the message first to be used to recieve'''
    bMsg=msg.encode()
    msgLength=str(len(bMsg)).encode()
    msgLength+=b' '*(64-len(msgLength))
    conn.send(msgLength)
    conn.send(bMsg)

def recieving(sock,q):
    '''Recieves the messages and adds them to the queue'''
    while True:
        amount=int(sock.recv(64).decode())
        msg=str(sock.recv(amount).decode())
        #print(msg)
        q.put(msg)