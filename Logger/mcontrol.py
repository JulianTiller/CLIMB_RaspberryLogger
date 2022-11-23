import sys
assert sys.version_info >= (3, 0),"Please run under python 3" # Stop execution if run under python 2

from _thread import start_new_thread
from datetime import datetime
import csv
import os.path
import time

import RPi.GPIO as GPIO
import socket
import os

from glog import *

def supply_3v3c(enable):
    if enable:
        GPIO.output(25, GPIO.HIGH) # 3V3-c
        glog_add("3V3-C Enabled")
    else:
        GPIO.output(25, GPIO.LOW) # 3V3-c
        glog_add("3V3-C Disabled")
    
def supply_3v3a(enable):
    if enable:
        GPIO.output(27, GPIO.HIGH) # 3V3-a
        glog_add("3V3-A Enabled")
    else:
        GPIO.output(27, GPIO.LOW) # 3V3-a
        glog_add("3V3-A Disabled")
        
def eled_enable(enable):
    if enable:
        GPIO.output(ELED_PIN, GPIO.HIGH) # 
    else:
        GPIO.output(ELED_PIN, GPIO.LOW) # 
        
        
def powercycle_obc():
    glog_add("Executing OBC powercycle")
    supply_3v3a(0)
    supply_3v3c(0)
    time.sleep(5)
    supply_3v3c(1)    
    time.sleep(1)
    supply_3v3a(1)
    glog_add("OBC powercycle done")
    powercycle_done()

def print_cmds():
    print('\nAvailable commands:')
    print('0...End program')
    print('1...Powercycle OBC')
    print('2...3V3-A enable')
    print('3...3V3-A disable')
    print('4...3V3-C enable')
    print('5...3V3-C disable')
    print('6...OBC supply enable')
    print('7...OBC supply disable')
    print('Select: ')

def main():
    global ELED_PIN
    
    # Check if logger is running
    ret = os.popen("pgrep -a python | grep 'logger.py'").read().strip()

    if(ret.count("logger.py") > 0): # 1 is this instance, more than one is an already running instance
        print("The logger is running. Be careful.")
        #exit()
    else:
        print("Manual logger control starting...")


    logberry_name = socket.gethostname() # "LogBerry0e" "LogBerry1" "LogBerry2"

    # Open global logger logfile
    glog_filename = '/home/pi/logger/logs/logberry_glog1.csv'
    glog_init(glog_filename)
    glog_add("Manual control started")

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(27, GPIO.OUT)
    #GPIO.output(27, GPIO.LOW) # 3V3-C, leave as is
    GPIO.setup(25, GPIO.OUT)
    #GPIO.output(25, GPIO.LOW) # 3V3-A, leave as is

    ELED_PIN = 4
    GPIO.setup(ELED_PIN, GPIO.OUT)
    GPIO.output(ELED_PIN, GPIO.LOW) # EXT-LED on LogBerry casing
    eled_enable(1)
    
    print_cmds()
    
    for line in sys.stdin:
    
        if 'Exit' == line.rstrip():
            break
            
        cmd = line.rstrip()
        if(cmd.isnumeric() == False):
            continue
        
        if(cmd == '0'):
            # End program
            break
        elif(cmd == '1'):
            powercycle_obc()
        elif(cmd == '2'):
            supply_3v3a(1)
        elif(cmd == '3'):
            supply_3v3a(0)
        elif(cmd == '4'):
            supply_3v3c(1)
        elif(cmd == '5'):
            supply_3v3c(0)
        elif(cmd == '6'):
            supply_3v3a(1)
            supply_3v3c(1)
        elif(cmd == '7'):
            supply_3v3a(0)
            supply_3v3c(0)
        else:
            print('Unknown CMD')

        print_cmds()

    glog_add("Manual control stopped.")
    glog_close()


if __name__ == '__main__':
    main()
