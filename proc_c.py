#!/usr/bin/env python
from node import node
import time


class proc_C(object):

    def __init__(self):
        self.name = "Node_C"
        self.address = "127.0.0.1"
        self.port = 5003

        
    def proc_c(self):
        test_C = node(self.name, self.address, self.port)
        time.sleep(4)
        test_C.init((self.address,self.port))
        print('starting init C')
        time.sleep(6)
        test_C.acquire()
        print("proc_c")
        time.sleep(2)
        print("releasing C")
        test_C.release()



if __name__ == "__main__":
    nodeC = proc_C()
    nodeC.proc_c()