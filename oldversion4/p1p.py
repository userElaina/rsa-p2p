from rsap2p import TCPp2p
from _config import *

a=TCPp2p(('0.0.0.0',23305),'user1','127.0.0.1')
a.start()

a.connect('user0',('127.0.0.1',23301))

time.sleep(2)
a.sendmsg('Hello world!','user0')

time.sleep(10)
a.closed('user0')

time.sleep(2)
print('END')
