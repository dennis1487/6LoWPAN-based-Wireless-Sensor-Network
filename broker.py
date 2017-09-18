import socket, sys, time

s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
s.bind(("", 31500))

while True:
    data, addr = s.recvfrom(2048)
    print "Received:", data, "from", addr
    s.sendto("Hi! I am Broker.", addr)