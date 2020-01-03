#!/usr/bin/env python
from node import node
import argparse
import time
import sys
import threading



# def __init__(self,args):
#     self.use_time = args.use_time
#     self.wait_time = args.wait_time
#     self.name = args.name
#     self.sponsor = (args.sponsor_addr, args.sponsor_port)
#     self.addr = args.addr
#     self.port = args.port

def runTest():
    nodeA = node("Node_A","0.0.0.0", 5000)
    nodeB = node("Node_B","0.0.0.0", 5001)
    nodeC = node("Node_C","0.0.0.0", 5002)

    
    threadB = threading.Thread(target = programB, args=(nodeB, ))
    threadC = threading.Thread(target = programC, args=(nodeC, ))
    threadA = threading.Thread(target = programA, args=(nodeA, ))
    threadB.start()
    threadC.start()
    threadA.start()

    quit()

def programA(node):
    node.acquire()
    print("proc_a")
    time.sleep(2)
    node.release()
    time.sleep(10)

def programB(node):
    time.sleep(5)
    node.acquire()
    print("proc_b")
    time.sleep(2)
    node.release()
    time.sleep(10)

def programC(node):
    time.sleep(6)
    node.acquire()
    print("proc_c")
    time.sleep(2)
    node.release()
    
    

if __name__ == "__main__":
    runTest()