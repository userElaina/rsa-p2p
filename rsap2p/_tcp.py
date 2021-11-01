import os
import socket
from userelaina._th import throws
from rsap2p._sc import RSAclient,RSAserver
from rsap2p._config import *

CORE=os.cpu_count()
THREAD=CORE<<1
SIZE=65536


class TCPclient(RSAclient):
    def __init__(self,server_addr:tuple,myname:str='tcpclient',gname:str='tcpserver'):
        RSAclient.__init__(self,server_addr,myname,gname)

    def basic_send(self,b:bytes):
        self.s.send(b)

    def basic_recv(self):
        return self.s.recv(SIZE)

    def start(self):
        self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.connect(self.addr)
        self.log.info('client('+self.myname+').connect('+repr(self.addr)+')')

    def close(self,code:int=0):
        self.s.close()
        RSAclient.close(self,code)



class TCPserver(RSAserver):
    def __init__(self,addr:tuple,myname:str='tcpserver',recvf=lambda x,y:GOOD):
        RSAserver.__init__(self,addr,myname,recvf)
        self.s=dict()

    def basic_send(self,b:bytes,addr:tuple):
        self.s[addr].send(b)

    def basic_recv(self,addr:tuple):
        return self.s[addr].recv(SIZE)

    def start(self,n:int=THREAD):
        self.n=n
        self.mian=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.mian.bind(self.addr)
        self.mian.listen(n)

    def run(self):
        _s,_addr=self.mian.accept()
        self.s[_addr]=_s
        self.log.info('server('+self.myname+').connect('+repr(_addr)+')')
        code=self.handshake(_addr)
        if code>=0:
            self.log.warning('server('+self.myname+').communicate('+repr(_addr)+')')
            while True:
                rb=self.recv(_addr)
                if rb<0:
                    code=rb
                    break
        self.close(_addr,code)

    def join(self):
        while True:
            self.run()

    def throws(self,n:int=CORE):
        n=self.n if n>self.n or n<0 else n
        for i in range(n):
            throws(self.join)

    def close(self,addr:str='rsa.client.0',code:int=0):
        self.lk.acquire()
        if addr in self.s:
            self.s[addr].close()
            del self.s[addr]
        self.lk.release()
        RSAserver.close(self,addr,code)