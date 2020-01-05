#!/usr/bin/env python
from node import node
import time



class proc_A(object):

    def __init__(self):
        self.name = "Node_A"
        self.address = '0.0.0.0'
        self.sponsor = (('127.0.0.1',5001)) 
        self.port = 5001

        
    def proc_a(self):
        test_A = node(self.name, self.address, self.port)
        test_A.init(self.sponsor)
        print('starting init in A')
        test_A.acquire()
        print("proc_a")
        time.sleep(2)
        print('Releasing A')
        test_A.release()
        time.sleep(10)
        print('waking')


if __name__ == "__main__":
    nodeA = proc_A()
    nodeA.proc_a()