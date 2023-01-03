import sys
assert sys.version_info >= (3, 0),"Please run under python 3" # Stop execution if run under python 2

from datetime import datetime
import time
import socket
import os
import psutil

from glog import tss

from logberry2telegram import logberry2telegram

def main():
    logberry_name = socket.gethostname() # "LogBerry0e" "LogBerry1" "LogBerry2"
    msg = '\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n'       \
          + logberry_name + ' startup at '+ tss()[:-7] +'\n'    \
          + '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
    
    time.sleep(3)
    print(msg)    
    try:
        tg = logberry2telegram(logberry_name,True)
        tg.send(msg)
    except:
        print('Telegram interface failed')  
        
if __name__ == '__main__':
    main()