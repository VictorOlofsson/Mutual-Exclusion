#!/usr/bin/env python
from node import node
import time




class proc_B(object):

    def __init__(self):
        self.name = "Node_B"
        self.address = "127.0.0.1"
        self.port = 5002

        
    def proc_b(self):
        test_B = node(self.name, self.address, self.port)
        time.sleep(3)
        test_B.init((self.address, self.port))
        print('starting init in B')
        time.sleep(5)
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