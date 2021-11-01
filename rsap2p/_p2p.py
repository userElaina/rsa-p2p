import os
import rsa
import time
import base64
from rsap2p._config import *
from rsap2p._tcp import TCPserver,TCPclient,THREAD

class TCPp2p(TCPserver):
    def __init__(self,addr:tuple,myname:str,ip:str,pth='./'):
        TCPserver.__init__(self,addr,myname)
        self.gsend=dict() # name : socket
        self.gsalt=dict() # name : salt
        # self.gname=dict() # name : addr
        # self.guest=dict() # name : public.key
        # self.gaddr=dict() # addr : name

        self.ip=ip
        self.pth=os.path.join(os.path.abspath(pth),myname)
        # self.setlog(level='debug',out=os.path.join(self.pth,myname+'.log'))
        # self.setlog(level='info',out=os.path.join(self.pth,myname+'.log'))
        # self.setlog(level='warning',out=os.path.join(self.pth,myname+'.log'))
        self.setlog(level='error',out=os.path.join(self.pth,myname+'.log'))

    def loadguests(self)->int:
        if not os.path.isdir(self.pth):
            return ERROR_PATH_NOT_FOUND
        for i in os.listdir(self.pth):
            j=os.path.join(pth,i)
            if not os.path.isdir(j):
                continue
            kpth=os.path.join(j,i+'.public.key')
            if not os.path.isfile(kpth):
                continue
            try:
                self.guest[i]=rsa.PublicKey.load_pkcs1(open(kpth,'rb').read())
            except:
                self.log.debug('rsa('+self.myname+').gf.load('+i+')::bad key')
                continue
            self.log.debug('rsa('+self.myname+').gf.load('+i+')')

    def start(self,n:int=THREAD):
        self.load(os.path.join(self.pth,self.myname+'.public.key'),os.path.join(self.pth,self.myname+'.private.key'))
        TCPserver.start(self,n)
        self.throws(n)

    def sendmsg(self,b:str,name:str)->int:
        if name not in self.gsend:
            self.log.error('p2p('+self.myname+').sendmsg('+name+')::NOT_FOUND')
            return ERROR_404
        return self.gsend[name].sendmsg(b)

    def checkf(self,b:bytes,addr:tuple)->int:
        self.log.debug('p2p('+self.myname+').check('+repr(addr)+')::'+repr(b))

        # MY_NAME ip.port.proactive.salt GC_NAME
        b=b.split(SPLIT,1)
        if len(b)!=2:
            return SERVER_WTF
        b=[b[0],]+b[1].rsplit(SPLIT,1)
        if len(b)!=3:
            return SERVER_WTF

        b=[i.decode('utf8') for i in b]
        if b[0]!=self.myname:
            return SERVER_WRONG_NAME
        code=GOOD
        if b[2] in self.gsend:
            try:
                _addr=b[1].rsplit('.',3)
                if _addr[2]!=PASSIVE:
                    raise RuntimeError
                if _addr[3]!=self.gsalt[b[2]]:
                    raise RuntimeError
            except:
                return IP_ADDRESS_SPOOFING
        else:
            try:
                _addr=b[1].rsplit('.',3)
                if _addr[2]!=PROACTIVE:
                    raise RuntimeError
                _salt=_addr[3]
                _addr=(_addr[0],int(_addr[1]),)
            except:
                return IP_ADDRESS_SPOOFING
            code=self.connect(b[2],_addr,PASSIVE,_salt)  
        self.gaddr[addr]=b[2]
        self.gname[b[2]]=addr
        return code

    def connect(self,gname:str,gsaddr:tuple=None,proactive:str=PROACTIVE,salt:str=None)->int:
        self.log.info('p2p('+self.myname+').connect('+repr(gsaddr)+')::'+proactive)
        _d=os.path.join(self.pth,gname)

        addrpth=os.path.join(_d,gname+'.addr')
        try:
            _l=open(addrpth,'rb').read().decode('utf8').split('\n')
            if _l==['',] or not _l:
                raise RuntimeError
        except:
            _l=list()
        if gsaddr is None:
            try:
                gsaddr=_l[-1].rsplit('.',1)
                gsaddr=(gsaddr[0],int(gsaddr[1]))
            except:
                return ERROR_NEED_ADDRESS
        else:
            _str=gsaddr[0]+'.'+str(gsaddr[1])
            if _str not in _l:
                open(addrpth,'ab').write(_str.encode('utf8')+b'\n')

        gs=TCPclient(gsaddr,self.myname,gname)
        try:
            gs.loadguest(os.path.join(_d,gname+'.public.key'))
        except:
            return ERROR_LOAD_PUBLIC_KEY
        # gs.setlog(level='debug',out=os.path.join(_d,gname+'.log'))
        # gs.setlog(level='info',out=os.path.join(_d,gname+'.log'))
        # gs.setlog(level='warning',out=os.path.join(_d,gname+'.log'))
        gs.setlog(level='error',out=os.path.join(_d,gname+'.log'))
        try:
            gs.start()
        except:
            return ERROR_404

        if salt is None:
            salt=base64.b64encode(os.urandom(64)).decode('utf8')
        self.gsalt[gname]=salt
        gs.setsalt(self.ip+'.'+str(self.addr[1])+'.'+proactive+'.'+salt)

        self.gsend[gname]=gs
        code=gs.handshake_proactive2()
        if code<0:
            del self.gsend[gname]
            return code
        else:
            return GOOD

    def handshake(self,addr:tuple)->int:
        self.log.info('p2p('+self.myname+').handshake('+repr(addr)+')')
        code=self.handshake_passive2(addr)
        if code<0:return code
        return GOOD

    def close(self,addr:tuple,code:int=0):
        self.lk.acquire()
        if addr in self.gaddr:
            name=self.gaddr[addr]
            if name in self.gsend:
                self.gsend[name].close(code)
                del self.gsend[name]
        self.lk.release()
        TCPserver.close(self,addr,code)

    def closed(self,name:str):
        self.close(self.gname[name],0)
