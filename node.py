#!/usr/bin/env python

import socket
import threading
from message import Message
import time



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
        self.outstanding_reply_count = 0
        self.requesting_cs = False
        self.init_done = False
        self.init_status = ""
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
            self.handle_unknown_node(args)  # Handle messages to nodes that is unknown/dead
        else: {
            Message.TYPE.REPLY      : self.handle_reply_message,
            Message.TYPE.REQUEST    : self.handle_request_message,
            Message.TYPE.DEAD       : self.handle_dead_message,
            Message.TYPE.INIT       : self.handle_init_message
        }[msg.type](args)

    # Handles unknown/dead nodes
    def handle_unknown_node(self, args):
        sender = args[0]
        content = args[0]
        dead = Message(Message.TYPE.DEAD, self.info,{"STATUS": "Trying to reinitialize"})
        self.msg_sender((sender['IP'],sender['PORT']), dead.prepare())


    def handle_reply_message(self,args):
        self.lock.acquire()
        # if(self.outstanding_reply_count > 0):
        #     outstanding_reply_count -= 1
        # if(self.outstanding_reply_count == 0):
        #     self.listener_event.set()
        #     self.listener_event.clear()
        self.timeoutTimer.cancel()
        self.timeoutTimer = threading.Timer(30.0, self.check_waiting_nodes)
        self.timeoutTimer.start()
        self.lock.release()


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
            self.reply_deferred[in_unique_name] = True
        else:
            reply = Message()
            to_send = reply.prepare(Message.TYPE.REPLY,self.info,{})
            self.msg_sender(in_unique_name,to_send)

    def check_waiting_nodes(self):
        pass
        # print("RA-MUTEX::TIMEOUT")
        # for node in self.awaiting_reply.keys():
        #     if self.awaiting_reply.get(node):
        #         mess = Message(Message.TYPE.ARE_YOU_THERE,self.info,{})
        #         self.send_message_to_node(node,mess.prepare())
        #         self.second_timeout = threading.Timer(1.0, self.wait_for_i_am_here)

    
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


    def handle_init_message(self, args):
        sender = args[0]
        content = args[1]
        address = args[2]
        if(content["ROLE"] == "NEW"):
            print("RA-MUTEX::INCOMING-NODE-TO-INIT")
            self.lock.aquire()
            if(len(self.nodes) == 0): # Check if first in queue
                self.init_done = True
            self.aquire()

            message = Message()
            if((self.nodes.has_key(sender["UNIQUENAME"])) or (self.info["UNIQUENAME"] == sender["UNIQUENAME"])):
                init_data = {"ROLE": "SPONSOR", "STATUS": "NOT UNIQUE"}
                send_to_new = message.prepare(Message.TYPE.INIT, self.info, init_data)
            else:
                send_to_nodes = message.prepare(Message.TYPE.INIT, self.info, {"ROLE": "NODE", "NEWDATA": sender})
                for node in self.nodes:
                    self.send_message_to_node(node,send_to_nodes)
                init_data = {"ROLE": "SPONSOR", "STATUS": "OK", "NODESDATA": self.nodes}
                send_to_new = message.prepare(Message.TYPE.INIT, self.info, init_data)
                self.nodes[sender["UNIQUENAME"]] = {"IP": sender["IP"], "PORT": sender["PORT"]}
                self.msg_sender((sender["IP"],sender["PORT"]),send_to_new)
                self.release()
                print("RA-MUTEX::INIT-DONE")
                self.lock.release()
        elif content["ROLE"] == "NODE":
             self.nodes[content["NEWDATA"]["UNIQUENAME"]] = { 'IP': content["NEWDATA"]['IP'], 'PORT': content["NEWDATA"]['PORT']}
        elif content["ROLE"] == "SPONSOR":
            self.init_status = content["STATUS"]
            if (self.init_status == "OK"):
                self.nodes = content["NODEDATA"]
                self.nodes[sender["UNIQUENAME"]] = { 'IP' : sender['IP'], 'PORT': sender['PORT']}
                self.init_done = True
            else:
                self.init_done = False
        self.listener_event.set()
        self.listener_event.clear()

    def delete_node(self, node):
        self.lock.acquire()
        if self.nodes.has_key(node):
            del self.nodes[node]
        if self.reply_deferred.get(node):
            del self.reply_deferred[node]
        if self.awaiting_reply.get(node):
            del self.awaiting_reply[node]
        if self.requesting_cs:
            if (self.outstanding_reply_count > 0):
                self.outstanding_reply_count -= 1
            if (self.outstanding_reply_count == 0):
                self.listener_event.set()
        self.lock.release()
                
    
    def wait_for_im_here(self):
        self.timeout_status = False
        self.timeout_event.set()
    
    def send_message_to_node(self, args):
        pass
    
    def acquire(self):
        self.lock.acquire()
        if not self.init_done:
            self.init.lock.release()
            return False
        if self.disposing:
            self.lock.release()
            return False
        
        #print "ACQUIRE"

        self.lock.acquire()
        self.requesting_cs = True
        self.seq_num = int(self.highest_seq_num) + 1
        self.outstanding_reply_count = len(self.nodes)
        
        if (self.outstanding_reply_count == 0):
            self.listening_event.set()
        
        mess = Message(Message.TYPE>REQUEST,self.inf0,{"SEQNUM":self.seqnum})

        for node in self.nodes.keys():
            self.awaiting_reply[node] = True
        self.lock.release()

        for node in self.nodes.keys():
            try:
                self.send_message_to_node(node, mess.prepare())
            except socket.err, msg:
                print("Error code: " + str(msg[0]) + ', Error message : ' + msg[1])
        print("RA-MUTEX:: Waiting for nodes Reply")
        self.timeoutTimer.cancel()
        self.timeoutTimer = threading.Timer(10.0, self.check_awaiting_nodes)
        self.timeoutTimer.start()
        self.listening_event.wait()
        self.listening_event.clear()
        self.lock.release()
        self.timeoutTimer.cancel()
        return True

    def release(self):
        if not self.init_done:
            return False
        self.requesting_cs = False
        for node in self.nodes.keys():
            if self.reply_deffered.get(node):
                self.reply_deffered[node] = False
                message = Message(Message.TYPE.REPLY,self.info, {})
                try:
                    self.send_message_to_node(node, message.prepare())
                except socket.error, msg:
                    print("Error code: " + str(msg[0]) + " , Error message: " + msg[1])
            return True

    
