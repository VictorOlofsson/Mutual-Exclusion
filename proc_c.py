#!/usr/bin/env python
from node import node
import time


def proc_C(node):
    time.sleep(6)
    node.acquire()
    print("proc_c")
    time.sleep(2)
    node.release()
    

if __name__ == "__main__":
    nodeC = node("Node_C","0.0.0.0", 5003)
    proc_C(nodeC)