import sys
import rsap2p

try:
    addr,name=(sys.argv[1],int(sys.argv[2]),),sys.argv[3]
except:
    addr,name=('127.0.0.1',23301),'user0'

try:
    rsap2p.SSHclient(('0.0.0.0',23305),'user1','127.0.0.1').joins(addr,name)
except:
    sys.exit(1)
