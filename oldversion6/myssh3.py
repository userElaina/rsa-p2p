import os
# import re
# import io
# import time 
# import shlex
import subprocess
from userelaina.th import throws

os.system('> 1.reg')
os.system('> 2.reg')
mian=subprocess.Popen('whoami > /dev/null',shell=True)

def _in():
    global mian
    while True:
        i=input()
        try:
            command=i.encode('utf8')+b'\n'
            mian.stdin.write(command)
            mian.stdin.flush()
        except:
            os.system('> 1.reg')
            os.system('> 2.reg')
            command=i+' >1.reg 2>2.reg'
            print('RUN',command)
            mian=subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )


def _out():
    r_out=b''
    r_err=b''
    running=True
    while True:
        if mian.poll() is not None:
            if running:
                print('#### ',end='',flush=True)
                running=False
        else:
            running=True

        l=open('1.reg','rb').read()
        if len(l)!=len(r_out):
            if len(l)>len(r_out):
                print(l[len(r_out):].decode('utf8'),end='',flush=True)
            r_out=l
        else:
            l=open('2.reg','rb').read()
            if len(l)!=len(r_err):
                if len(l)>len(r_err):
                    print(l[len(r_err):].decode('utf8'),end='',flush=True)
                r_err=l

throws(_out)

_in()
