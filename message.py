#!/usr/bin/env python
import json

SUPPORTED_MSG_TYPES = ["REPLY", "REQUEST", "DEAD", "INIT", "ARE_YOU_THERE", "HIGHEST_SEQ_NUM", "YES_I_AM_HERE"] # Declares message types as a list 

### Enumerate class###
class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


### Class for handling messages ###
class Message(object):
    TYPE = Enum(SUPPORTED_MSG_TYPES)

    # Initializes the message types
    def __init__(self, msg_type=None, msg_sender=None, msg_content=None):
        if (msg_type != None):
            if (msg_type not in SUPPORTED_MSG_TYPES):
                raise Exception("Unkown message type")
        self.type = msg_type
        self.sender = msg_sender
        self.content = msg_content

    # Returns a string with 'Message type', 'Message sender' and 'Message content'
    def __str__(self):
        return "Message: TYPE = " + ("None" if (self.type == None) else self.type) \
                + " FROM = " + ("None" if (self.type == None) else str(self.sender)) \
                + " CONTENT = " + ("None" if (self.content == None) else str(self.content))

    # Prepares message using json and catches exceptions for bad arguments
    def prepare(self, msg_type=None, msg_sender=None, msg_content=None):
        if (msg_type == None and msg_sender == None and msg_content == None):
            pass
        elif (msg_type != None and msg_sender != None and msg_content != None):
            self.__init__(msg_type,msg_sender,msg_content)
        else:
            raise Exception("Bad Parse Args")
        return json.dumps({"TYPE": self.type, "FROM": self.sender, "CONTENT": self.content})

    # Parse the messages using json sets values for type, sender and content
    def parse(self,msg):
        parsed_msg = json.loads(msg)
        if (parsed_msg["TYPE"] not in SUPPORTED_MSG_TYPES):
            raise Exception("Unknow message type")
        self.type = parsed_msg["TYPE"]
        self.sender = parsed_msg["FROM"]
        self.content = parsed_msg["CONTENT"]

