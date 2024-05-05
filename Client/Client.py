from tkinter import *
from tkinter import font
from os import path
import traceback
from ClientFunc import socketConnect,send,recieving
from threading import Thread
import queue

PATH=path.dirname(path.abspath(__file__))

class App(Tk):
    '''General class for my tk windows'''
    def __init__(self):
        #Inheriting from tk
        super().__init__()
        #General Window Settings
        self.iconbitmap(PATH+"\BUCKET.ico")
        self.config(bg="black")
        self.options={'padx':5,'pady':5,'bg':'black'}
        self.labelFont=font.Font(family="Roboto")
        self.messageFont=font.Font(family="Roboto",underline=True)
        self.entryFont=font.Font(family="lato",weight="bold",size=12)
        self.listFont=font.Font(family="Roboto",size=12)

class Login(App):
    '''Login window'''
    def __init__(self):
        super().__init__()
        #Window Management
        self.title("Login")
        self.eval("tk::PlaceWindow . centre")
        self.resizable(False,False)
        #Weight
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=1)
        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        #Labels
        self.lblUsername=Label(self,font=self.labelFont,text="Username:",fg='limegreen',**self.options)
        self.lblUsername.grid(column=0,row=0)
        self.lblIp=Label(self,font=self.labelFont,text="IP Address\n(or device name):",fg='limegreen',**self.options)
        self.lblIp.grid(column=0,row=1)
        self.message=Message(self,text="Enter Something",width=150,font=self.messageFont,fg='firebrick',**self.options)
        self.message.grid(column=0,row=3,sticky=NSEW)
        #Entries
        #UsernameEntry
        self.usernameEntryFrame=Frame(self,**self.options)
        self.usernameEntry=Entry(self.usernameEntryFrame,bg="gray25",fg="limegreen",font=self.entryFont)
        self.usernameEntry.pack(fill=X,expand=True)
        self.usernameEntryFrame.grid(column=1,row=0,sticky=NSEW)
        self.usernameEntry.bind("<Return>",lambda event: self.enter())
        #IPEntry
        self.IPEntryFrame=Frame(self,**self.options)
        self.IPEntry=Entry(self.IPEntryFrame,bg="gray25",fg="limegreen",font=self.entryFont)
        self.IPEntry.pack(fill=X,expand=True)
        self.IPEntryFrame.grid(column=1,row=1,sticky=NSEW)
        self.IPEntry.bind("<Return>",lambda event: self.enter())
        #Button
        self.Submit=Button(text="Submit",font=self.labelFont,command=lambda: self.enter(),bg="gray25",fg="limegreen")
        self.Submit.grid(column=1,row=3,sticky=NSEW)
        self.mainloop()
        
    def enter(self):
        '''Grabs username and ip, connects to the server and checks the username isnt taken'''
        self.username=self.usernameEntry.get().strip()
        self.ip=self.IPEntry.get().strip()
        if not self.username:
            self.changeMsg("Username cannot be empty")
        elif len(self.username)>10:
            self.changeMsg("Username cannot be longer than 10 characters")
        elif not self.ip:
            self.changeMsg("IP cannot be empty")
        else:
            smth=socketConnect(self.username,self.ip)
            if smth==False:
                self.changeMsg("Could not connect")
            elif smth=="Taken":
                self.changeMsg("Username Taken")
            else:
                self.sock,self.colour=smth[0],smth[1]
                self.withdraw()
                chat=Chat(username=self.username,ip=self.ip,colour=self.colour,sock=self.sock)

    def changeMsg(self,msg):
        '''Changes the message widget to the entered message'''
        self.message.config(text=msg)

class Chat(App):
    '''Chat window'''
    def __init__(self,username,ip,colour,sock):
        super().__init__()
        #Actual initialization
        self.username=username
        self.ip=ip     
        self.colour=colour
        self.sock=sock
        self.userList={}
        self.q=queue.Queue()
        #Window Management
        self.title("Chat")
        self.minsize(width=500,height=300)
        self.columnconfigure(0,weight=9)
        self.columnconfigure(1,weight=1)
        self.rowconfigure(0,weight=49)
        self.rowconfigure(1,weight=1)
        self.grid_columnconfigure(1,minsize=100)
        #Chatbox
        self.chatFrame=Frame(self,borderwidth=0,highlightthickness=0,**self.options)
        self.chatFrame.columnconfigure(0,weight=99)
        self.chatFrame.columnconfigure(1,weight=1)
        self.chatFrame.rowconfigure(0,weight=98)
        self.chatFrame.rowconfigure(1,weight=1)
        self.chat=Text(self.chatFrame,state=DISABLED,bg="black",fg="limegreen",borderwidth=0,highlightthickness=0)
        self.chatScroll=Scrollbar(self.chatFrame,orient=VERTICAL,command=self.chat.yview)
        self.chatScroll.config(command=self.chat.yview)
        self.seeBottom=Button(self.chatFrame,text="↓",command=self.down)
        self.chat.grid(row=0,column=0,rowspan=3,sticky=NSEW)
        self.chatScroll.grid(row=0,column=1,sticky=NSEW)
        self.seeBottom.grid(row=1,column=1,sticky=NSEW)
        self.chat.config(yscrollcommand=self.chatScroll.set)
        self.chatFrame.grid(row=0,column=0,sticky=NSEW)
        #MessageBox
        self.msgFrame=Frame(self,bg="white")
        self.msgFrame.columnconfigure(0,weight=1)
        self.msgFrame.columnconfigure(1,weight=4)
        self.msgFrame.rowconfigure(0,weight=1)
        self.msgbox=Entry(self.msgFrame,font=self.entryFont,bg="gray25",fg="limegreen")
        self.deletebtn=Button(self.msgFrame,text="Delete",command=self.delete)
        self.deletebtn.grid(row=0,column=0,sticky=NSEW)
        self.msgbox.grid(row=0,column=1,sticky=NSEW)
        self.msgFrame.grid(row=1, column=0,sticky=NSEW)
        self.msgbox.bind("<Return>",lambda event: (self.sendMsg()))
        #Send
        self.send=Button(self,text="Send",font=self.labelFont,command=(lambda: self.sendMsg()),bg="gray25",fg="limegreen")
        self.send.grid(column=1,row=1,sticky=NSEW)
        #Right Side
        self.rightFrame=Frame(self)
        self.rightFrame.rowconfigure(0,weight=1)
        self.rightFrame.rowconfigure(1,weight=1)
        #UserList
        self.userFrame=Frame(self.rightFrame)
        self.userFrame.columnconfigure(0,weight=49)
        self.userFrame.columnconfigure(1,weight=1)
        self.userFrame.rowconfigure(0,weight=1)
        self.userFrame.rowconfigure(1,weight=29)
        self.userLabel=Label(self.userFrame,text="User List")
        self.userListbox=Listbox(self.userFrame,bg="black",fg="limegreen",font=self.listFont,justify=CENTER,height=10,selectmode=SINGLE,width=12)
        self.userListbox.bind('<<ListboxSelect>>',lambda event: (self.userListClick()))
        self.userScroll=Scrollbar(self.userFrame,orient=VERTICAL,command=self.chat.yview)
        self.userScroll.config(command=self.userListbox.yview)
        self.userListbox.config(yscrollcommand=self.userScroll.set)
        self.userListbox.grid(row=1,column=0,sticky=NSEW)
        self.userScroll.grid(row=1,column=1,sticky=NSEW)
        self.userLabel.grid(row=0,column=0,columnspan=2,sticky=NSEW)
        self.userFrame.grid(row=1,column=0,sticky=NSEW)
        #Details section
        self.details=Frame(self.rightFrame,bg="black")
        self.detailLabel=Label(self.details,text="Server & User Details",font=self.messageFont,fg=self.colour,**self.options)
        self.IPLabel=Label(self.details,text=f"Server IP: {self.ip}",font=self.labelFont,fg=self.colour,**self.options)
        self.usernameLabel=Label(self.details,text=f"Username: {self.username}",font=self.labelFont,fg=self.colour,**self.options)
        self.colourLabel=Label(self.details,text=f"User Colour: {self.colour}",font=self.labelFont,fg=self.colour,**self.options)
        self.detailLabel.pack()
        self.IPLabel.pack()
        self.usernameLabel.pack()
        self.colourLabel.pack()
        self.details.grid(row=0,column=0,sticky=NSEW)
        self.rightFrame.grid(row=0,column=1,sticky=NSEW)
        #Running Start Func
        self.focus()
        self.t = Thread(target=recieving,daemon=True,args=(self.sock,self.q))
        self.t.start()
        self.after(100, self.listen)

    def sendMsg(self):
        '''Sends the message to the server'''
        msg=self.getMsg()
        send(msg,self.sock)

    def getMsg(self):
        '''Gets message from the message box and deletes the contents'''
        msg=self.msgbox.get().strip()
        self.msgbox.delete(0,END)
        return msg
    
    def delete(self):
        '''Clears the message box'''
        self.msgbox.delete(0,END)

    def down(self):
        '''Focuses the chat on the bottom msg'''
        self.chat.see(END)

    def insertChat(self,msg,colour):
        '''Prints the message to the chatbox'''
        self.chat.tag_config(colour,foreground=colour)
        self.chat.config(state='normal')
        self.chat.insert('end',msg+"\n",(colour))
        self.chat.config(state='disabled')
        self.chat.grid()

    def userListClick(self):
        '''Puts the username into the message box'''
        user=self.userListbox.get(ANCHOR)
        self.msgbox.insert(END,user)

    def userListUpdate(self):
        '''Deletes the entire queue and adds all of the list back.'''
        self.userListbox.delete(0,'end')
        for i in range(len(self.userList)):
            self.userListbox.insert(i,list(self.userList.keys())[i])
            colour=self.userList[list(self.userList.keys())[i]]
            self.userListbox.itemconfig(i,foreground=colour)

    def listen(self):
        '''Check if there is something in the queue.'''
        try:
            self.res = self.q.get(0)
            if self.res[0]=='@':
                self.res=self.res.strip("@").split(",")
                print(self.res)
                self.userList[self.res[0]]=self.res[1]
                self.userListUpdate()
            else:
                self.res=self.res.split("|",1)
                self.insertChat(self.res[1],self.res[0])
            self.after(100, self.listen)
        except queue.Empty:
            self.after(100, self.listen)

if __name__ == '__main__':
    login=Login()