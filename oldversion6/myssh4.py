import os
import subprocess
from userelaina.th import throws,lock,unlock

replace_dict={
    'python':'python -i',
    'python3':'python3 -i',
}

for i in replace_dict.copy():
    replace_dict[i.encode('utf8')]=replace_dict[i].encode('utf8')

class MySSH:
    def __init__(self,name:str=''):
        self.name=name

        os.makedirs('sshregs',exist_ok=True)
        os.system('>sshregs/'+name+'.1')
        os.system('>sshregs/'+name+'.2')
        os.system('>sshregs/'+name+'.3')
        os.remove('sshregs/'+name+'.3')
        
        self.mian=subprocess.Popen(
            '/bin/bash > sshregs/'+name+'.1 2> sshregs/'+name+'.2',
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.mian.stdin.write(b'echo $$ > sshregs/'+name.encode('utf8')+b'.3\n')
        self.mian.stdin.flush()
        self.mian.stdin.write(b'cd ~\n')
        self.mian.stdin.flush()

        while not os.path.exists('sshregs/'+name+'.3'):
            None
        self.checkid='ps --ppid '+open('sshregs/'+name+'.3','rb').read().decode('utf8').strip()+' | wc -l'

        self.r_out=b''
        self.r_err=b''
        self.mian.stdin.write(b'echo -n "MySSH@'+name.encode('utf8')+b'$ " >&2\n')
        self.mian.stdin.flush()

    def ain(self,b:bytes)->int:
        if b in replace_dict:
            b=replace_dict[b]
        try:
            command=b+b'\n'
            self.mian.stdin.write(command)
            self.mian.stdin.flush()
            self.mian.stdin.write(b'echo -n "MySSH@'+self.name.encode('utf8')+b'$ " >&2\n')
            self.mian.stdin.flush()
            return 0
        except:
            return 1

    def aout(self)->dict:
        ans={
            'out':'',
            'err':'',
        }
        code=0

        if self.mian.poll() is not None:
            code|=4

        l_err=open('sshregs/'+self.name+'.2','rb').read()
        l_out=open('sshregs/'+self.name+'.1','rb').read()

        if len(l_out)>len(self.r_out):
            code|=1
            ans['out']=l_out[len(self.r_out):].decode('utf8')
            self.r_out=l_out

        if len(l_err)>len(self.r_err):
            code|=2
            ans['err']=l_err[len(self.r_err):].decode('utf8')
            self.r_err=l_err

        ans['code']=code
        return ans


if __name__=='__main__':
    a=MySSH()

    def _in():
        while True:
            i=input().strip().encode('utf8')
            a.ain(i)

    def _out():
        while True:
            ans=a.aout()
            code=ans['code']
            if ans['out']:
                print(ans['out'],end='',flush=True)
            if ans['err']:
                print(ans['err'],end='',flush=True)
            if ans['code']&4:
                exit()

    throws(_in)
    _out()
