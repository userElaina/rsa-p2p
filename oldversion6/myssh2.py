import os
import sys
import time
import subprocess
from userelaina.th import throws

os.makedirs('sshregs',exist_ok=True)
os.chdir('sshregs')

os.system('>1.reg')
os.system('>2.reg')
os.system('>3.reg')
os.remove('3.reg')
mian=subprocess.Popen(
    '/bin/bash > 1.reg 2> 2.reg',
    shell=True,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

mian.stdin.write(b'echo $$ > 3.reg\n')
mian.stdin.flush()
mian.stdin.write(b'cd ~\n')
mian.stdin.flush()

while not os.path.exists('3.reg'):
    time.sleep(1)
pid=open('3.reg','rb').read().decode('utf8').strip()
ck='ps --ppid '+pid+' | wc -l'
print(ck)

r_kid=2

def _in():
    global mian,r_kid
    while True:
        i=input().encode('utf8')
        r_kid=2
        try:
            command=i+b'\n'
            mian.stdin.write(command)
            mian.stdin.flush()
        except:
            sys.exit(0)


def _out():
    global r_kid
    _n=0
    r_out=b''
    r_err=b''
    running=True
    while True:
        _n+=1
        if mian.poll() is not None:
            if running:
                running=False
            else:
                print('Total:',_n)
                sys.exit(0)

        l_kid=int(subprocess.Popen(ck,shell=True,stdout=subprocess.PIPE).stdout.readline().decode('utf8').strip())
        l_err=open('2.reg','rb').read()
        l_out=open('1.reg','rb').read()

        if len(l_out)>len(r_out):
            print(l_out[len(r_out):].decode('utf8'),end='',flush=True)
            r_out=l_out

        if len(l_err)>len(r_err):
            print(l_err[len(r_err):].decode('utf8'),end='',flush=True)
            r_err=l_err

        if l_kid==1 and r_kid==2:
            print('qwq# ',end='',flush=True)
            r_kid=1

throws(_in)

_out()
