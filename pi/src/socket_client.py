import threading
import time

__author__ = 'pv'

import asyncore
import socket
import sys



#### Client
class TwitterClient(asyncore.dispatcher):
    buffer = ""

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def send_command(self, command):
        print "Sending command : " + command
        self.buffer = command

    def handle_close(self):
        self.close()

    def handle_read(self):
        print self.recv(8192)

    def writable(self):
        return len(self.buffer) > 0

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]


if __name__ == "__main__":

    # Create a TCP/IP socket
    client = TwitterClient('localhost', 6969)
    try:
        # Send data
        message = sys.argv[1]
        print >> sys.stderr, 'sending "%s"' % message
        client.send_command(message)
        asyncore.loop(count=1)
    finally:
        print >> sys.stderr, 'closing socket'
        # sock.close()