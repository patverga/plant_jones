__author__ = 'pv'

import socket
import sys

if __name__ == "__main__":

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('localhost', 10000)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)

    try:
        # Send data
        message = sys.argv[0]
        print >>sys.stderr, 'sending "%s"' % message
        sock.sendall(message)

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()
