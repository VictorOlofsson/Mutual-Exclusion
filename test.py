#!/usr/bin/env python
from node import node
import argparse
import time
import sys

APP_NAME = "Ra_Test"


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
        
        time.sleep(self.wait_time)
        test.acquire()
        print(self.name)
        time.sleep(2)
        test.release()
        time.sleep(10)


if __name__ == "__main__":
    test = RaTest(parseArgs())
    test.runTest()