import os
from rsap2p import RSAobj

pth=os.path.join(os.path.dirname(__file__),'uu')

for i in range(256):
    name='user'+str(i)
    d=os.path.join(pth,name)
    a=RSAobj()
    a.setlog('debug')
    a.new(4096)
    a.save(os.path.join(d,name+'.public.key'),os.path.join(d,name+'.private.key'))
