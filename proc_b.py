#!/usr/bin/env python
from node import node
import time




class proc_B(object):

    def __init__(self):
        self.name = "1"
        self.address = "127.0.0.1"
        self.port = 5002

        
    def proc_b(self):
        time.sleep(2)
        print('starting init in B')
        test_B = node(self.name, self.address, self.port)
        test_B.init((self.address, self.port))
        while True: 
            time.sleep(5)
            print("NODE::" + self.name + "::ACQUIRING_RESOURCE")
            test_B.acquire()
            print("proc_b")
            time.sleep(2)
            print("releasing B")
            test_B.release()
            time.sleep(10)
            print('waking')


if __name__ == "__main__":
    nodeB = proc_B()
    nodeB.proc_b()