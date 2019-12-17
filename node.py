#!/usr/bin/env python

import socket
import threading
from Ricart_Agrawala import ricart_agrawala as ra
from message import Message
import argparse
import time

APP_NAME = "Ra_Test"

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

    
    def handle_dead_message(self):
        pass


    def handle_init_message(self, args):
        pass

    def delete_node(self):
        pass
    
    def wait_for_im_here(self):
        pass



def parseArgs():
    parser = argparse.ArgumentParser(prog=APP_NAME, usage='%(prog)s [options]')
    parser.add_argument('--sponsor_addr','-r', type=str, required = False, default = '127.0.0.1', help='sponsor address')
    parser.add_argument('--sponsor_port','-i', type=int, default = None, help='sponsor port')
    parser.add_argument('--use_time','-u',type=int,required	= True, help="Using resource time")
    parser.add_argument('--wait_time','-w',type=int,required = True, help="Idle time")
    parser.add_argument('--name','-n',type=str,required =True, help="Unique Node Name")
    parser.add_argument('--addr','-a',type=str,required =False, default = '', help="node address")
    parser.add_argument('--port','-p',type=int,required =False, default = 0, help="node port")
    return parser.parse_args()

class RaTest(object):
    def __init__(self,args):
        self.use_time = args.use_time
        self.wait_time = args.wait_time
        self.name = args.name
        self.sponsor = (args.sponsor_addr, args.sponsor_port)
        self.addr = args.addr
        self.port = args.port

    def runTest(self):
        test = node(self.name,self.addr, self.port)
        if (self.sponsor[0] != None ) and (self.sponsor[1] != None):
            print("Node ::" + self.name + "::INITIALIZATION")
            test.init(self.sponsor)
        print("NODE::" + self.name + "::READY")
        while(True):
            print("NODE::" + self.name + "::IDLE")
            time.sleep(self.wait_time)
            print("NODE::" + self.name + "::ACQUIRING_RESOURCE")
            test.acquire()
            print("NODE::" + self.name + "::USING_RESOURCE")
            time.sleep(self.use_time)
            print("NODE::" + self.name + "::USING_DONE")
            print("NODE::" + self.name + "::RELEASING_RESOURCE")
            test.release()
        



if __name__ == "__main__":
    test = RaTest(parseArgs())
    test.runTest()
