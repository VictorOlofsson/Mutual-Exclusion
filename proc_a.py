#!/usr/bin/env python
from node import node
import time




class proc_A(object):

    def __init__(self):
        self.name = "Sponsor"
        self.address = '127.0.0.1'
        self.sponsor = (('127.0.0.1',5001)) 
        self.port = 5001

        
    def proc_a(self):
        time.sleep(1)
        test_A = node(self.name, self.address, self.port)
        # if (self.sponsor[0] != None ) and (self.sponsor[1] != None):
        #     print("Node ::" + self.name + "::INITIALIZATION")
        test_A.init(self.sponsor)
        #print("NODE::" + self.name + "::READY")
        while True:
            #print("NODE::" + self.name + "::IDLE")
            #print("NODE::" + self.name + "::ACQUIRING_RESOURCE")
            test_A.acquire()
            print("proc_a")
            time.sleep(2)
            #print('Releasing A')
            test_A.release()
            time.sleep(10)
            #print('waking')
        
   

if __name__ == "__main__":
    nodeA = proc_A()
    nodeA.proc_a()      

