import os
import re
from rsap2p._p2p import TCPp2p
from userelaina.th import throws
from userelaina.pthc import col2str,fastlog

_white='\x1b[0m'

error_codes={
    403:'Forbidden',
    404:'Not_Found',
    405:'Method_Not_Allowed',
    415:'Unsupported_Media_Type',
}


def _splitcmd(x:str)->tuple:
    x=x.split(' ',1)+['',]
    x1=x[0].strip().lower()
    x2=x[1].strip()
    return (x1,x2)


class TCPp2p_CUI(TCPp2p):
    def __init__(self,
        addr:tuple,
        myname:str,
        ip:str,
        pth='./',
        color_pwd:str='green',
        color_err:str='red',
        color_now:str='cyan',
        color_usr:str='yellow',
    ):
        TCPp2p.__init__(self,addr,myname,ip,pth)

        self.pwd=myname

        self.__log=fastlog('cui',level='quiet',out=os.path.join(self.pth,myname+'_cui.log'),save_old=False)
        self.__col_pwd=col2str(color_pwd)
        self.__col_err=col2str(color_err)
        self.__col_now=col2str(color_now)
        self.__col_usr=col2str(color_usr)



    def lg(self,s:all):
        s=repr(s)
        self.__log.debug(s)

    def pt(self,s:str=None):
        res='None...'
        if s:
            s=str(s)
            res=re.sub('\x1b\[[0-9]+m','',s)
            print('\r'+s+' '*(len(self.pwd)+2-len(res)))
        self.__log.info(res)
        print('\r'+self.__col_pwd+self.pwd+':'+_white+' ',end='')

    def er(self,s:str,code:int)->str:
        s=str(s)
        _s=error_codes[code]+': '+s
        _ws=' '*(len(self.pwd)+2-len(_s))
        print('\r'+self.__col_err+error_codes[code]+_white+': '+s+_ws)
        self.__log.error(s)
        print('\r'+self.__col_pwd+self.pwd+'#'+_white+' ',end='')


    def recvmsg(self,b:bytes=b'',addr:all='wtf'):
        name=self.gaddr[addr]
        if name==self.pwd.split('/')[-1]:
            _h=self.__col_now
        else:
            _h=self.__col_usr
        self.pt(_h+name+':'+_white+' '+b.decode('utf8'))
        return TCPp2p.recvmsg(self,b,addr)

    def cmd_clear(self):
        print('\x1b[256F\x1b[0J',end='')
        self.pt()

    def cmd_reboot(self):
        self.cmd_clear()

    def cmd_cd(self,pth:str):
        if pth in self.gname:
            self.pwd=self.myname+'/'+pth
        else:
            self.er(pth,404)
        self.pt()

    def cmd_ls(self):
        for i in self.gname:
            self.pt(i)
        self.pt()

    def cmd_connect(self,s:str):
        s=s.split(' ')
        addr=s[1].rsplit(':',1)
        self.connect(s[0],(addr[0],int(addr[1]),),)
        self.pt()

    def cmd(self,command:str):
        if command.startswith('/'):
            x=_splitcmd(command)
            self.lg(str(x))
            if x[0]=='/cd':
                self.cmd_cd(x[1])
            elif x[0]=='/ls':
                self.cmd_ls()
            elif x[0]=='/connect':
                self.cmd_connect(x[1])
            return

        elif self.pwd==self.myname:
            self.er(command,405)
        else:
            self.sendmsg(command,self.pwd.split('/')[-1])
        self.pt()

    def joins(self):
        self.cmd_reboot()
        self.start()
        while True:
            command=input().strip()
            code=self.cmd(command=command)
