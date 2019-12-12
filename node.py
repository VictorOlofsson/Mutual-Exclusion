#!/usr/bin/env python

import socket
import threading
from Ricart_Agrawala import ricart_agrawala as ra
from message import Message

BUFSIZE = 1024


DEFAULT_HOST = '127.0.0.1' #standard loopback interface address (localhost)
DEFAULT_PORT = 5555 #port listened on (Non-privilged ports are  > 1023)

class node(object):
        
    def __init__(self, node_name, IP, PORT):
        self.seq_num = 0 
        self.highest_seq_num = 0 
        self.nodes = {}
        self.info = {}
        self.lock = threading.Lock()
        self.listener_event = threading.Event()
        self.lock.acquire()
        self.info['IP'] = IP
        self.info['PORT'] = PORT
        self.info['NAME'] = node_name
        self.lock.release()
        thread = threading.Thread(target = self.msg_listener)
        thread.start()


    def msg_sender(self, address, msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(address)
        s.send(msg)
        s.close()


    def msg_listener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #lock process
        self.lock.acquire()
        s.bind((self.info['IP'], self.info['PORT']))
        address, port = s.getsockname()
        self.info['IP'] = address
        self.info['PORT'] = port
        print("Socket is bound to %s" % port)
        self.lock.release()  #release process
        self.listener_event.set()
        self.listener_event.clear() #put socket into listening mode 
        s.listen(5)
        print('Socket is listening')

        while True:
            client, address = s.accept()
            print("Got a connection from", address)
            thread = threading.Thread(target = self.msg_handle_dispatcher, args = ({client, address}))
            thread.start()
            client.send("Thank you for sending")


    def msg_handle_dispatcher(self, socket, address):
        data = socket.recv(BUFSIZE)
        msg = Message()
        msg.parse(data)
        args = (msg.sender, msg.content, address)
        
        if ((msg.type != Message.TYPE.INIT) and (msg.sender['NAME']  not in self.msg.nodes())):
            self.handle_unknown_node(args)
        else: {                                                 # Might want to add more message types
            Message.TYPE.REPLY      : self.handle_reply_message,
            Message.TYPE.REQUEST    : self.handle_request_message,
            Message.TYPE.DEAD       : self.handle_dead_message,
            Message.TYPE.INIT       : self.handle_init_message
        }[msg.type](args)


    def handle_unknown_node(self, args):
        sender = args[0]
        content = args[0]
        dead = Message(Message.TYPE.DEAD, self.info,{"STATUS": "Trying to reinitialize"})
        self.msg_sender((sender['IP'],sender['PORT']), dead.prepare())



    def handle_reply_message(self,args):
        self.lock.acquire()
        
        self.lock.release()


    def handle_request_message(self,args):
        pass

    
    def handle_dead_message(self):
        pass


    def handle_init_message(self, args):
        pass
