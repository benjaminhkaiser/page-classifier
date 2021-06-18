#!/usr/bin/env python3
# DO NOT PRINT TO STDOUT ANYWHERE IN THIS CODE
# IT INTERFERES WITH MESSAGING

import sys
import json
import struct

# Read a message from stdin and decode it.
def getMessage():
    rawLength = sys.stdin.buffer.read(4)
    if len(rawLength) == 0:
        sys.exit(0)
    messageLength = struct.unpack('@I', rawLength)[0]
    #print("messageLength: {0}".format(messageLength))
    message = sys.stdin.buffer.read(messageLength).decode('utf-8')
    return json.loads(message)

# Encode a message for transmission, given its content.
def encodeMessage(message_content):
    encoded_content = json.dumps(message_content).encode("utf-8")
    encoded_length = struct.pack('=I', len(encoded_content))
    #print("encoded_length: {0}".format(encoded_length))
    #  use struct.pack("10s", bytes), to pack a string of the length of 10 characters
    return {'length': encoded_length, 'content': struct.pack(str(len(encoded_content))+"s", encoded_content)}

# Send an encoded message to stdout
def sendMessage(encodedMessage):
    sys.stdout.buffer.write(encodedMessage['length'])
    sys.stdout.buffer.write(encodedMessage['content'])
    sys.stdout.buffer.flush()

#sendMessage(encodeMessage("Connected."))
receivedMessage = getMessage()
sendMessage(encodeMessage("Got it!"))
msg = receivedMessage.split("&&&&&")
filename = "".join([c for c in msg[0] if c.isalpha()
        or c.isdigit() or c == ' ']).rstrip()

with open("/home/bkaiser/temp/savePageData/{0}.txt".format(filename), 'w') as f:
    f.write(receivedMessage)
