#!/usr/bin/env python
from node import node
import time


class proc_C(object):

    def __init__(self):
        self.name = "2"
        self.address = "127.0.0.1"
        self.port = 5003

        
    def proc_c(self):
        time.sleep(3)
        print('starting init C')
        test_C = node(self.name, self.address, self.port)
        test_C.init((self.address, self.port))

        while True:
            time.sleep(6)
            print("NODE::" + self.name + "::ACQUIRING_RESOURCE") 
            test_C.acquire()
            print("proc_c")
            time.sleep(2)
            print("releasing C")
            test_C.release()



if __name__ == "__main__":
    nodeC = proc_C()
    nodeC.proc_c()