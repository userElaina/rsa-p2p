import os
import rsa
import hashlib
from userelaina.pthc import Archive,fastlog

class RSAobj():
    def __init__(self,myname:str='rsaobj',gname:str='gobj'):
        self.__public=None
        self.__private=None
        self.guest=None

        self.myname=myname
        self.gname=gname
        self.log=fastlog(name=myname,out=None,save_old=False)

    def err(self,code:int,msg:all=None):
        self.log.error(str(code)+'::'+str(msg))

    def myhash(self,x:bytes)->bytes:
        return hashlib.sha512(self.gname.encode('utf8')+x+self.myname.encode('utf8')).digest()

    def ghash(self,x:bytes)->bytes:
        return hashlib.sha512(self.myname.encode('utf8')+x+self.gname.encode('utf8')).digest()

    def setlog(self,level:str='warn',out:str=None,err:str=None,):
        del self.log
        self.log=fastlog(name=self.myname,level=level,out=out,err=err,save_old=False)

    def new(self,length:int=4096):
        self.__public,self.__private=rsa.newkeys(length)
        self.log.debug('rsa('+self.myname+').new('+str(length)+')')

    def loads(self,public:bytes,private:bytes):
        self.__public=rsa.PublicKey.load_pkcs1(public)
        self.__private=rsa.PrivateKey.load_pkcs1(private)
        self.log.debug('rsa('+self.myname+').m.loads(public,private)')

    def loadsguest(self,k:bytes):
        self.guest=rsa.PublicKey.load_pkcs1(k)
        self.log.debug('rsa('+self.myname+').g.loads(public)')

    def load(self,public_pth:str,private_pth:str):
        self.loads(open(public_pth,'rb').read(),open(private_pth,'rb').read())
        self.log.debug('rsa('+self.myname+').m.load(public,private)::'+public_pth)

    def loadguest(self,guest_pth:str):
        self.loadsguest(open(guest_pth,'rb').read())
        self.log.debug('rsa('+self.myname+').g.load(public)::'+guest_pth)

    def save(self,public_pth:str,private_pth:str):
        Archive().new(public_pth,b=self.__public.save_pkcs1())
        Archive().new(private_pth,b=self.__private.save_pkcs1())
        self.log.debug('rsa('+self.myname+').m.save(public,private)::'+public_pth)
        return 0

    def saveguest(self,guest_pth:str):
        if os.path.exists(guest_pth):
            return -1
        open(guest_pth,'wb').write(self.guest.save_pkcs1())
        self.log.debug('rsa('+self.myname+').g.save(public)::'+guest_pth)

    def self_intercourse(self):
        self.guest=self.__public

    def getpublic(self)->bytes:
        return self.__public.save_pkcs1()

    def decrypt(self,b:bytes)->bytes:
        return rsa.decrypt(b,self.__private)

    def encrypt(self,b:bytes)->bytes:
        return rsa.encrypt(b,self.guest)
