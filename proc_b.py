#!/usr/bin/env python
from node import node
import time


def proc_B(node):
    time.sleep(5)
    node.acquire()
    print("proc_b")
    time.sleep(2)
    node.release()
    time.sleep(10)


if __name__ == "__main__":
    nodeB = node("Node_B","0.0.0.0", 5002)
    proc_B(nodeB)