import os
import time
import socket
import base64

from _th import throws_ex,throws

n=os.cpu_count()
t=10

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.bind(('127.0.0.1',23301))
s.listen(os.cpu_count()<<1)

_count=0
def f():
	global _count
	while True:
		ss,ext=s.accept()
		print('connect:',ext)
		while True:
			rd=ss.recv(1024)
			if not rd:
				break
			_count+=1
			print('receive:',rd)
			sd=base64.b64encode(rd)
			ss.send(sd)
			print('send:',sd)
		ss.close()
		print('close:',ext)

for i in range(n):
	throws(f)

while True:
	_count=0
	time.sleep(t)
	print('count:',_count)

