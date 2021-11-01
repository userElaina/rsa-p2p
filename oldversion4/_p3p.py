from rsap2p import TCPp2p
from _config import *

a=TCPp2p(('0.0.0.0',23303),'user3','192.168.233.67')
a.start()

a.connect('user0',('192.168.233.64',23301))

time.sleep(2)
a.sendmsg('Hello world!','user0')

time.sleep(10)
a.closed('user0')

time.sleep(2)
print('END')
