import rsa
import hashlib
import threading
from rsap2p._config import *
from rsap2p._obj import RSAobj


class RSAclient(RSAobj):
    def __init__(self,server_addr:str='rsa.server.0',myname:str='rsaclient',gname:str='rsaserver'):
        RSAobj.__init__(self,myname,gname)
        self.addr=server_addr

    def im(self,send,recv):
        self.basic_send=send
        self.basic_recv=recv

    def sendmsg(self,b:str)->int:
        self.log.info('['+self.myname+'->'+self.gname+']'+b)
        return self.send(b.encode('utf8'))

    def send(self,send_b:bytes)->int:
        try:
            self.basic_send(self.encrypt(send_b))
        except:
            return CLIENT_SEND_BROKEN
        self.log.debug('client('+self.myname+').send('+repr(self.addr)+')::'+repr(send_b))

        try:
            recv_b=self.basic_recv()
        except:
            return CLIENT_RECV_BROKEN
        # self.log.debug('client('+self.myname+').recv('+repr(self.addr)+')::'+repr(recv_b))
        if recv_b!=self.myhash(send_b):
            return CLIENT_CHECKSUM_FAILURE
        return GOOD

    def setsalt(self,salt:str='rsaserver')->bytes:
        # GS_NAME salt MY_NAME
        b=[self.gname,salt,self.myname]
        b=[i.encode('utf8') for i in b]
        b=SPLIT.join(b)
        self.handshake_b=b
        return b

    def handshake_proactive1(self)->int:
        self.log.debug('client('+self.myname+').handshake.proactive1('+repr(self.addr)+')')
        send_b=self.handshake_b

        try:
            self.basic_send(send_b)
        except:
            return CLIENT_SEND_BROKEN
        self.log.debug('client('+self.myname+').send.first('+repr(self.addr)+')::'+repr(send_b))

        try:
            recv_b=self.basic_recv()
        except:
            return CLIENT_RECV_BROKEN
        self.log.debug('client('+self.myname+').recv.key('+repr(self.addr)+')::'+repr(recv_b))

        try:
            self.loadsguest(recv_b)
        except:
            return CLIENT_RECV_BAD_KEY
        return GOOD


    def handshake_proactive2(self)->int:
        self.log.debug('client('+self.myname+').handshake.proactive2('+repr(self.addr)+')')
        send_b=self.handshake_b
        recv_int=self.send(send_b)
        return recv_int


    def handshake(self,salt:str='rsaserver')->bool:
        self.log.info('client('+self.myname+').handshake('+repr(self.addr)+')')
        self.setsalt(salt)
        code=self.handshake_proactive1()
        if code<0:return code
        code=self.handshake_proactive2()
        if code<0:return code
        return GOOD

    def close(self,code:int=0):
        self.log.warning('client('+self.myname+').close('+repr(self.addr)+').code('+repr(code)+')::'+repr(self.gname))



class RSAserver(RSAobj):
    def __init__(self,addr:str='rsa.server.0',myname:str='rsaserver',recvf=lambda x,y:GOOD):
        RSAobj.__init__(self,myname,dict())
        self.recvf=recvf
        self.addr=addr
        # self.gname=dict() # name : addr
        self.guest=dict() # name : public.key
        self.gaddr=dict() # addr : name
        self.lk=threading.Lock()

    def recvmsg(self,b:bytes=b'',addr:all='rsa.client.0'):
        self.log.info('['+self.myname+'<-'+self.gaddr[addr]+']'+b.decode('utf8'))
        return self.recvf(b,addr)

    def ghash(self,x:bytes,addr:all='rsa.client.0'):
        return hashlib.sha512(self.myname.encode('utf8')+x+self.gaddr[addr].encode('utf8')).digest()

    def loadsguest(self,k:bytes,gname:str='rsaclient'):
        self.guest[gname]=rsa.PublicKey.load_pkcs1(k)
        self.log.debug('rsa('+self.myname+').gs.loads('+repr(gname)+')')

    def loadguest(self,guest_pth:str,gname:str='rsaclient'):
        self.loadsguest(open(guest_pth,'rb').read(),gname)
        self.log.debug('rsa('+self.myname+').gs.load('+repr(gname)+')')


    def recv(self,addr:str='rsaclient')->bytes:
        try:
            recv_b=self.basic_recv(addr)
            if not recv_b:
                raise RuntimeError
        except:
            return SERVER_RECV_BROKEN

        try:
            recv_b=self.decrypt(recv_b)
        except:
            return SERVER_DECRYPT
        self.log.debug('server('+self.myname+').recv('+repr(addr)+')::'+repr(recv_b))
        code=self.recvmsg(recv_b,addr)
        if code<0:
            return code

        send_b=self.ghash(recv_b,addr)
        try:
            self.basic_send(send_b,addr)
        except:
            return SERVER_SEND_BROKEN
        # self.log.debug('server('+self.myname+').send('+repr(addr)+')::'+repr(send_b))
        return GOOD


    def checkf(self,b:bytes,addr:str='rsa.client.0')->int:
        # MY_NAME salt GC_NAME
        b=b.split(SPLIT,1)
        if len(b)!=2:
            return SERVER_WTF
        b=[b[0],]+b[1].rsplit(SPLIT,1)
        if len(b)!=3:
            return SERVER_WTF

        b=[i.decode('utf8') for i in b]
        if b[0]!=self.myname:
            return SERVER_WRONG_NAME
        if b[2] not in self.gname:
            return SERVER_STRANGE_USER
        return GOOD


    def handshake_passive1(self,addr:str='rsa.client.0')->int:
        self.log.debug('server('+self.myname+').handshake.passive1('+repr(addr)+')')
        try:
            recv_b=self.basic_recv(addr)
            if not recv_b:
                raise RuntimeError
        except:
            return SERVER_RECV_BROKEN
        self.log.debug('server('+self.myname+').recv.first('+repr(addr)+')::'+repr(recv_b))

        # MY_NAME first GC_NAME
        recv_b=recv_b.split(SPLIT,1)
        if len(recv_b)!=2:
            return SERVER_WTF
        recv_b=[recv_b[0],]+recv_b[1].rsplit(SPLIT,1)
        if len(recv_b)!=3:
            return SERVER_WTF
        recv_b=[i.decode('utf8') for i in recv_b]
        if recv_b[0]!=self.myname:
            return SERVER_WRONG_NAME

        _gname=recv_b[2]
        self.gname[_gname]=addr
        self.gaddr[addr]=_gname

        send_b=self.getpublic()
        try:
            self.basic_send(send_b,addr)
        except:
            return SERVER_SEND_BROKEN
        self.log.debug('server('+self.myname+').send.key('+repr(addr)+')::'+repr(send_b))
        return GOOD


    def handshake_passive2(self,addr:str='rsa.client.0')->int:
        self.log.debug('server('+self.myname+').handshake.passive2('+repr(addr)+')')
        try:
            recv_b=self.basic_recv(addr)
        except:
            return SERVER_RECV_BROKEN

        try:
            recv_b=self.decrypt(recv_b)
        except:
            return SERVER_DECRYPT
        self.log.debug('server('+self.myname+').recv.ping-pong'+repr(addr)+'::'+repr(recv_b))

        code=self.checkf(recv_b,addr)
        if code<0:
            return code

        send_b=self.ghash(recv_b,addr)
        try:
            self.basic_send(send_b,addr)
        except:
            return SERVER_RECV_BROKEN
        self.log.debug('server('+self.myname+').send('+repr(addr)+')::'+repr(send_b))
        return GOOD


    def handshake(self,addr:str='rsa.client.0'):
        self.log.info('server('+self.myname+').handshake('+repr(addr)+')')
        code=self.handshake_passive1(addr)
        if code<0:return code
        code=self.handshake_passive2(addr)
        if code<0:return code
        return GOOD

    def close(self,addr:str='rsa.client.0',code:int=0):
        self.lk.acquire()
        name=None
        if addr in self.gaddr:
            name=self.gaddr[addr]
            if name in self.guest:
                del self.guest[name]
            if name in self.gname:
                del self.gname[name]
            del self.gaddr[addr]
        self.lk.release()
        self.log.warning('server('+self.myname+').close('+repr(addr)+').code('+repr(code)+')::'+repr(name))
