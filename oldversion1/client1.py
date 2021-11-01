import time
import socket
import random

n=5
t=10

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect(('127.0.0.1',23301))
while True:
	l=[random.randint(0,100) for i in range(n)]
	_sum=sum(l)/t
	l=[i/_sum for i in l.copy()]
	for i in l:
		sd=str(i).encode('utf8')
		print('send:',sd)
		s.send(sd)
		rd=s.recv(1024)
		print('receive:',rd)
		time.sleep(i)

s.close()
