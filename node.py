#!/usr/bin/env python

import socket
import threading
from message import Message
import time
import sys



BUFSIZE = 1024


DEFAULT_HOST = '127.0.0.1' #standard loopback interface address (localhost)
DEFAULT_PORT = 5555 #port listened on (Non-privilged ports are  > 1023)

class node(object):

    # Finnished    
    def __init__(self, name, IP, PORT):
        self.seq_num = 0 
        self.highest_seq_num = 0
        self.outstanding_reply_count = 0
        self.requesting_cs = False
        self.disposing = False
        self.reply_deffered = {}
        self.awaiting_reply = {}
        self.nodes_highest_seq_num = {}
        self.nodes = {}
        self.info = {}
        self.init_done = False
        self.init_status = ""
        self.lock = threading.Lock()
        self.init_lock = threading.RLock()
        self.listener_event = threading.Event()
        self.timeoutTimer = threading.Timer(30.0, self.check_waiting_nodes)
        self.lock.acquire()
        self.info['IP'] = IP
        self.info['PORT'] = PORT
        self.info['UNIQUENAME'] = name
        self.lock.release()
        thread = threading.Thread(target = self.msg_listener)
        thread.start()
        # Wait for listener thread init
        self.listener_event.wait()

    # Finnished
    def msg_sender(self, address, msg):
        mess = bytes(msg, 'UTF-8')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(address)
        s.send(mess)
        s.close()

    # Finnished
    def msg_listener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #lock process
        self.lock.acquire()
        s.bind((self.info['IP'], self.info['PORT']))
        address, port = s.getsockname()
        self.info['IP'] = ("127.0.0.1" if address == "0.0.0.0" else address )
        self.info['PORT'] = port
        #print("Socket is bound to %s" % port)
        self.lock.release()  #release process
        self.listener_event.set()
        self.listener_event.clear() #put socket into listening mode 
        s.listen(2)
        #print("Socket is listening %s" % address)

        while True:
            client, address = s.accept()
            thread = threading.Thread(target = self.msg_handle_dispatcher, args = ((client, address)))
            thread.start()

    # Finnished
    def msg_handle_dispatcher(self, socket, address):
        data = socket.recv(BUFSIZE)
        msg = Message()
        msg.parse(data)
        args = (msg.sender, msg.content, address)
        if ((msg.type != Message.TYPE.INIT) and (msg.sender['UNIQUENAME'] not in self.msg.nodes())):
            self.handle_unknown_node(args)  # Handle messages to nodes that is unknown/dead
        else: 
            {
            Message.TYPE.REPLY              : self.handle_reply_message,
            Message.TYPE.REQUEST            : self.handle_request_message,
            Message.TYPE.DEAD               : self.handle_dead_message,
            Message.TYPE.INIT               : self.handle_init_message,
            Message.TYPE.HIGHEST_SEQ_NUM    : self.handle_highest_seq_num,
            Message.TYPE.YES_I_AM_HERE      : self.handle_yes_i_am_here,
            Message.TYPE.ARE_YOU_THERE      : self.handle_are_you_there
            }[msg.type](args)

    # Handles unknown/dead nodes
    def handle_unknown_node(self, args):
        sender = args[0]
        content = args[1]
        dead = Message(Message.TYPE.DEAD, self.info,{"STATUS": "Trying to reinitialize"})
        self.msg_sender((sender['IP'],sender['PORT']), dead.prepare())

    # Finnished
    def handle_reply_message(self,args):
        self.lock.acquire()
        if(self.outstanding_reply_count > 0):
            self.outstanding_reply_count -= 1
        if(self.outstanding_reply_count == 0):
            self.listener_event.set()
            self.listener_event.clear()
        self.timeoutTimer.cancel()
        self.timeoutTimer = threading.Timer(30.0, self.check_waiting_nodes)
        self.timeoutTimer.start()
        self.lock.release()

    # Finnished
    def handle_request_message(self,args):
        sender = args[0]
        content = args[1]
        in_seq_num = content["SEQNUM"]
        in_unique_name = sender["UNIQUENAME"]
        self.lock.acquire()
        self.highest_seq_num = max(self.highest_seq_num, in_seq_num)
        defer_it = (self.requesting_cs and \
            ((in_seq_num > self.seq_num) or ((in_seq_num == self.seq_num) and \
                in_unique_name > self.info["UNIQUENAME"])))
        self.lock.release()
        if defer_it:
            self.reply_deffered[in_unique_name] = True
        else:
            reply = Message()
            to_send = reply.prepare(Message.TYPE.REPLY,self.info,{})
            self.send_message_to_node(in_unique_name,to_send)

    # Finished
    def check_waiting_nodes(self):
        print("RA-MUTEX::TIMEOUT")
        print(time.time())
        for node in self.awaiting_reply.keys():
            if self.awaiting_reply.get(node):
                mess = Message(Message.TYPE.ARE_YOU_THERE,self.info,{})
                self.send_message_to_node(node,mess.prepare())
                self.second_timeout = threading.Timer(1.0, self.wait_for_i_am_here)
                print('found node' + self.info)
                self.second_timeout.start()
                self.listener_event.wait()
                self.listener_event.clear()
                if (self.timeout_status == False):
                    self.delete_node(node)
    # Finished
    def handle_dead_message(self, args):
        print("RA-MUTEX::Net detected node falure::" + str(args[1]))
        sender = args[0]
        content = args[1]
        if (content["STATUS"] == "REMOVE"):
            self.delete_node(content["NODE"])
        elif (content["STATUS"] == "RE_INIT"):
            self.lock.acquire()
            self.init_done = False
            self.init_status = "RE_UNIT"
            self.lock.release()

    # Finished
    def handle_init_message(self, args):
        sender = args[0]
        content = args[1]
        address = args[2]
        if(content["ROLE"] == "NEW"):
            #print("RA-MUTEX::INCOMING-NODE-TO-INIT")
            self.init_lock.acquire()
            if(len(self.nodes) == 0): # Check if first in queue
                self.init_done = True
            self.acquire()
            message = Message()
            if((sender["UNIQUENAME"] in self.nodes) or (self.info["UNIQUENAME"] == sender["UNIQUENAME"])):
                init_data = {"ROLE": "SPONSOR", "STATUS": "NOT UNIQUE"}
                send_to_new = message.prepare(Message.TYPE.INIT, self.info, init_data)
            else:
                send_to_nodes = message.prepare(Message.TYPE.INIT, self.info, {"ROLE": "NODE", "NEWDATA": sender})
                print('role sponsor')
                for node in self.nodes:
                    self.send_message_to_node(node,send_to_nodes)
                init_data = {"ROLE": "SPONSOR", "STATUS": "OK", "NODESDATA": self.nodes}
                send_to_new = message.prepare(Message.TYPE.INIT, self.info, init_data)
                self.nodes[sender["UNIQUENAME"]] = {"IP": sender["IP"], "PORT": sender["PORT"]}
            
            self.msg_sender((sender['IP'],sender['PORT']),send_to_new)
            self.release()
            #print("RA-MUTEX::INIT-DONE")
            self.init_lock.release()
        elif content["ROLE"] == "NODE":
            self.nodes[content["NEWDATA"]["UNIQUENAME"]] = { 'IP': content["NEWDATA"]['IP'], 'PORT': content["NEWDATA"]['PORT']}
        elif content["ROLE"] == "SPONSOR":
            #print("role sponsor")
            self.init_status = content["STATUS"]
            if (self.init_status == "OK"):
                self.nodes = content["NODESDATA"]
                self.nodes[sender["UNIQUENAME"]] = { 'IP' : sender['IP'], 'PORT': sender['PORT']}
                self.init_done = True
            else:
                self.init_done = False
            self.listener_event.set()
            self.listener_event.clear()

    # Finished
    def delete_node(self, node):
        self.lock.acquire()
        if node in self.nodes:
            del self.nodes[node]
        if self.reply_deffered.get(node):
            del self.reply_deffered[node]
        if self.awaiting_reply.get(node):
            del self.awaiting_reply[node]
        if self.requesting_cs:
            if (self.outstanding_reply_count > 0):
                self.outstanding_reply_count -= 1
            if (self.outstanding_reply_count == 0):
                self.listener_event.set()
        self.lock.release()
                
    # Finished
    def wait_for_i_am_here(self):
        self.timeout_status = False
        self.timeout_event.set()
    
    # Finished
    def send_message_to_node(self, node, message):
        try:
            self.msg_sender((self.nodes[node]['IP'],self.nodes[node]['PORT']),message)
        except socket.error as msg:
            print("RA-MUTEX::Detected Node Failure::Deleting node: ", node)
            self.delete_node(node)
            dead = Message(Message.TYPE.DEAD,self.info,{"STATUS": "REMOVE", "NODE": node})
            for node in self.nodes.keys():
                self.send_message_to_node(node,dead.prepare())
    # Finished
    def handle_are_you_there(self, args):
        sender = args[0]
        content = args[1]
        mess = Message(Message.TYPE.YES_I_AM_HERE,self.info,{})
        self.send_message_to_node(sender["UNIQUENAME"], mess.prepare())

        if (self.reply_deffered.get(sender["UNIQUENAME"])==False):
            reply = Message()
            to_send = reply.prepare(Message.TYPE.REPLY,self.info,{})
            self.send_message_to_node(sender["UNIQUENAME"],to_send)
    
    # Finished    
    def handle_highest_seq_num(self, args):
        sender = args[0]
        content = args[1]
        if (content["STATUS"]=="GET"):
            mess = Message(Message.TYPE.HIGHEST_SEQ_NUM,self.info,{"STATUS":"RESPONSE", "VALUE": self.highest_seq_num})
            self.send_message_to_node(sender["UNIQUENAME"],mess.prepare())
        elif (content["STATUS"]=="RESPONSE"):
            self.nodes_highest_seq_num[sender["UNIQUENAME"]] = int(content["VALUE"])
            if len(self.nodes_highest_seq_num) == len(self.nodes):
                self.listener_event.set()
                self.listener_event.clear()
        
    # Finished
    def handle_yes_i_am_here(self, args):
        sender = args[0]
        content = args[1]
        self.second_timeout.cancel()
        self.timeout_status = True
        self.listener_event.set()

    # Finished
    def init(self, address):
        mess = Message(Message.TYPE.INIT,self.info,{"ROLE":"NEW"})
        self.msg_sender(address,mess.prepare())
        self.listener_event.wait()
        for node in self.nodes.keys():
            mess = Message(Message.TYPE.HIGHEST_SEQ_NUM, self.info,{"STATUS": "GET"})
            self.send_message_to_node(node, mess.prepare())
        self.listener_event.wait()
        highest_num = -1
        for num in self.nodes_highest_seq_num:
            if self.nodes_highest_seq_num[num] > highest_num: highest_num = self.nodes_highest_seq_num[num]
        self.highest_seq_num = highest_num
        return (self.init_done, self.init_status)

    # Finished
    def acquire(self):
        self.init_lock.acquire()
        if self.init_done != True:
            self.init_lock.release()
            print("init not done")
            return False
        if self.disposing:
            self.init_lock.release()
            print('disposing')
            return False
        
        self.lock.acquire()
        self.requesting_cs = True
        print('critical section now true')
        self.seq_num = int(self.highest_seq_num) + 1
        self.outstanding_reply_count = len(self.nodes)
        
        if (self.outstanding_reply_count == 0):
            self.listener_event.set()
        
        mess = Message(Message.TYPE.REQUEST,self.info,{"SEQNUM":self.seq_num})

        for node in self.nodes.keys():
            self.awaiting_reply[node] = True
        self.lock.release()
        for node in self.nodes.keys():
            try:
                self.send_message_to_node(node, mess.prepare())
            except socket.error as msg:
                print("Error code: " + str(msg[0]) + ', Error message : ' + msg[1])
        #print("RA-MUTEX::Waiting for nodes Reply")
        self.timeoutTimer.cancel()
        self.timeoutTimer = threading.Timer(10.0, self.check_waiting_nodes)
        self.timeoutTimer.start()
        self.listener_event.wait()
        self.listener_event.clear()
        self.init_lock.release()
        self.timeoutTimer.cancel()
        return True

    # Finished
    def release(self):
        if self.init_done != True:
            return False
        self.requesting_cs = False
        for node in self.nodes.keys():
            if self.reply_deffered.get(node):
                self.reply_deffered[node] = False
                message = Message(Message.TYPE.REPLY,self.info, {})
                try:
                    self.send_message_to_node(node, message.prepare())
                except socket.error as msg:
                    print("Error code: " + str(msg[0]) + " , Error message: " + msg[1])
        return True

    # Finished
    def dispose(self):
        self.disposing = True
        if self.requesting_cs: self.release()
        mess = Message(Message.TYPE.DEAD, self.info,{"STATUS": "REMOVE", "NODE": self.info["UNIQUENAME"]})
        for node in self.nodes:
            try:
                self.send_message_to_node(node, mess.prepare())
            except socket.error as msg:
                print("Error code" + str(msg[0] + ', Error Message : ' + msg[1]))
        self.disposing = False
        self.init_done = False
