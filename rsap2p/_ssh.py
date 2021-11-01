import json
from rsap2p._p2p import TCPp2p
from rsap2p._myssh import MySSH
from userelaina.th import throws
from userelaina.pthc import fastlog

class SSHserver(TCPp2p):
    def __init__(self,
        addr:tuple,
        myname:str,
        ip:str,
        pth='./',
    ):
        TCPp2p.__init__(self,addr,myname,ip,pth)
        self.pwd=myname
        self.gsshd=dict() # addr : MySSH

    def recvmsg(self,b:bytes=b'',addr:all='wtf'):
        self.gsshd[addr].ain(b)
        return TCPp2p.recvmsg(self,b,addr)

    def __always_send(self,name:str):
        while True:
            ans=self.gsshd[self.gname[name]].aout()
            if ans['code']:
                self.sendmsg(json.dumps(ans),name)

    def run(self):
        _s,addr=self.mian.accept()
        self.s[addr]=_s
        self.log.info('server('+self.myname+').connect('+repr(addr)+')')
        code=self.handshake(addr)
        if code>=0:
            self.log.warning('server('+self.myname+').communicate('+repr(addr)+')')
            self.gsshd[addr]=MySSH(self.gaddr[addr])
            throws(self.__always_send,self.gaddr[addr])
            while True:
                rb=self.recv(addr)
                if rb<0:
                    code=rb
                    break
        self.close(addr,code)

    def joins(self):
        self.start()
        input()


class SSHclient(TCPp2p):
    def __init__(self,
        addr:tuple,
        myname:str,
        ip:str,
        pth='./',
    ):
        TCPp2p.__init__(self,addr,myname,ip,pth)
        self.pwd=myname

    def recvmsg(self,b:bytes=b'',addr:all='wtf'):
        ans=json.loads(b)
        code=ans['code']
        if ans['out']:
            print(ans['out'],end='',flush=True)
        if ans['err']:
            print(ans['err'],end='',flush=True)
        if ans['code']&4:
            print('MySSH@'+self.gaddr[addr]+'$ ',end='',flush=True)
        if ans['code']&8:
            self.close(addr)
        return TCPp2p.recvmsg(self,b,addr)

    def joins(self,addr,name):
        self.start()
        self.connect(name,addr)
        while True:
            try:
                command=input().strip()
            except:
                command='exit'
            self.sendmsg(command,name)
