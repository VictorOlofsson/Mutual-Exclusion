#!/usr/bin/env python
from node import node
import time


def proc_A(node):
    node.acquire()
    print("proc_a")
    time.sleep(2)
    node.release()
    time.sleep(10)


if __name__ == "__main__":
    nodeA = node("Node_A","0.0.0.0", 5001)
    proc_A(nodeA)