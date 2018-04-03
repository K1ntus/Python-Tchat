import socket
import select
import threading


#port7

#partie1
s = socket.socket(family=socket.AF_INET6, type=socket.SOCK_DGRAM, proto=0, fileno=None)
s.bind(('',7777))

while 1:
    (msg, addr) = s.recvfrom(1500) 
    s.sendto(bytes(1500),addr)

    print(s.recv(1500))
