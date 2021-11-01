from rsap2p import TCPp2p
from _config import *

a=TCPp2p(('0.0.0.0',23301),'user0','127.0.0.1')

a.start()

time.sleep(10)
a.sendmsg('Hello world!','user3')
a.sendmsg('Hello world!','user1')

_count=0
while True:
    time.sleep(5)
    _count+=1
    print(_count)