import sys
assert sys.version_info >= (3, 0),"Please run under python 3" # Stop execution if run under python 2

from _thread import start_new_thread
from datetime import datetime, timedelta
import csv
import os.path
import time
import RPi.GPIO as GPIO
import socket
import os
import psutil
import signal

from glog import *

from logberry2telegram import logberry2telegram

from serial_logger import serial_logger_worker
from serial_logger import serlog_stop
from serial_logger import serlog_read_keepalive
from serial_logger import powercycle_done
from serial_logger import request_powercycle

from event_logger import event_logger_worker
from event_logger import eventlog_read_keepalive
from event_logger import eventlog_stop
from event_logger import get_resets

from periodic_logger import periodic_logger_worker
from periodic_logger import perlog_read_keepalive
from periodic_logger import perlog_stop
from periodic_logger import get_snapshot

ret = os.popen("pgrep -a python | grep 'logger.py'").read().strip()

if(ret.count("logger.py") > 1): # 1 is this instance, more than one is an already running instance
    print("An instance of the logger is already running. Please stop it first.")
    quit()
else:
    print("Starting new logger instance...")

# Logger configuration
logberry_name = socket.gethostname() # "LogBerry0e" "LogBerry1" "LogBerry2"
use_telegram = 1
#use_eventlogger =  0
powercycle_counter = 0

def get_free_disk_space():
    statvfs = os.statvfs('/home/pi/logger')
    total = statvfs.f_frsize * statvfs.f_blocks     # Size of filesystem in bytes
    free = statvfs.f_frsize * statvfs.f_bavail      # Number of free bytes 
    return 'Available disk: ' + "{:.2f}".format(free/1073741824) + ' Gibytes of ' + "{:.2f}".format(total/1073741824) + ' Gibytes'



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
    global powercycle_counter
    powercycle_counter = powercycle_counter + 1
    tg.send('Executing OBC powercycle (' + str(powercycle_counter) + ')')
    glog_add('Executing OBC powercycle (' + str(powercycle_counter) + ')')
    supply_3v3a(0)
    supply_3v3c(0)
    time.sleep(5)
    supply_3v3c(1)    
    time.sleep(1)
    supply_3v3a(1)
    glog_add("OBC powercycle done")
    powercycle_done()
    
def terminateProcess(signalNumber, frame):
    print ('(SIGTERM) terminating the process')
    eled_enable(0)
    glog_add("SIGTERM interrupted program execution")
    glog_add("LogBerry Logger stopped.")
    tg.send("SIGTERM interrupted program execution - Logger stopped.")
    glog_close()
    sys.exit('Terminated by SIGTERM')

glog_filename = '/home/pi/logger/logs/logberry_glog.csv'
glog_init(glog_filename)

ts_logger_start = datetime.now()

# Init telegram connection
try:
    tg = logberry2telegram(logberry_name,use_telegram)
    glog_add("Telegram interface initialized (Enabled: " + str(use_telegram) +")")
except:
    glog_add("Telegram interface connection failed");

GPIO.setmode(GPIO.BCM)

glog_add("Initializing GPIOs")
GPIO.setup(25, GPIO.OUT)
#GPIO.output(27, GPIO.LOW) # 3V3-C, leave as is
GPIO.setup(27, GPIO.OUT)
#GPIO.output(25, GPIO.LOW) # 3V3-A, leave as is

ELED_PIN = 4
GPIO.setup(ELED_PIN, GPIO.OUT)
GPIO.output(ELED_PIN, GPIO.LOW) # EXT-LED on LogBerry casing

# Activate power to OBC
supply_3v3c(1) # Enable backup supply
time.sleep(1)
supply_3v3a(1) # Enable main supply
eled_enable(1)


# Start all the threads
glog_add('Starting threads')
start_new_thread(serial_logger_worker,())
time.sleep(0.5)
start_new_thread(event_logger_worker,())
time.sleep(0.5)
start_new_thread(periodic_logger_worker,())
glog_add("Waiting for threads to run...")
time.sleep(0.5)

# Wait for all threads to start
for i in range(25):
    if(serlog_read_keepalive() > 0 and perlog_read_keepalive() > 0 and eventlog_read_keepalive() > 0):
        glog_add('Threads are running')        
        break
    time.sleep(0.2)
    
if(i >= 24):
    glog_add('At least one thread could not be started')
    glog_close()
    quit()

# Everything seems to be up and running
tg.send("------------------------------------------------\nLogger started")
ts_led = datetime.now()
led_toggler = 0

ts_keepalive = datetime.now() 
ts_snapshot = datetime.now()- timedelta(seconds = 5395)
serlog_keepalive = 0
perlog_keepalive = 0

signal.signal(signal.SIGTERM, terminateProcess)

try:
    while True:
        time.sleep(0.1)
        ts = datetime.now()
        
        if((ts - ts_led).total_seconds() > 0.5): # Regular activity blink
            ts_led = ts
            if led_toggler:
                eled_enable(0)
                led_toggler = 0
            else:
                eled_enable(1) 
                led_toggler = 1
                
        if((ts - ts_snapshot).total_seconds() > 5400):
            ts_snapshot = ts;   
            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            mem = psutil.virtual_memory()
            logger_uptime = (datetime.now() - ts_logger_start)
            tg.send('Snapshot - ' + tss()[:-7] + ':\n' + get_snapshot() + '\nResets: ' + str(get_resets()) + '\nPowercycles: ' + str(powercycle_counter) \
                    + '\n' + get_free_disk_space() + '\n' + "RAM available: {:.2f}".format(mem.available/1e6) +' Mbyte\n'\
                    +'Uptime: ' + "{:.2f}".format(uptime.seconds/3600) + ' hours, ' + "Logger uptime: {:.2f}".format(logger_uptime.seconds/3600) + ' hours')
        
        if((ts - ts_keepalive).total_seconds() > 10):
            ts_keepalive = ts;
            
            if(request_powercycle() == 1):
                powercycle_obc()
            
            #print(serlog_keepalive)
            #print(serlog_read_keepalive())
            if(serlog_keepalive == serlog_read_keepalive()):
                glog_add("Error in serlog execution (keepalive failed)")
                tg.send("Error during regular execution of serial logger (keepalive failed)")
                serlog_stop()
                start_new_thread(serial_logger_worker,())

            #else:
                #print("serlog ok")    
            
            #print(perlog_keepalive)
            #print(perlog_read_keepalive())
            if(perlog_keepalive == perlog_read_keepalive()):
                glog_add("Error in perlog execution (keepalive failed)")
                tg.send("Error during regular execution of periodic logger (keepalive failed)")
                perlog_stop()
                start_new_thread(periodic_logger_worker,())
                
            #else:
                #print("perlog ok")

            serlog_keepalive = serlog_read_keepalive()
            perlog_keepalive = perlog_read_keepalive()
        
except KeyboardInterrupt:
    print('User interrupted program execution')

eled_enable(0)
glog_add("User interrupted program execution")
glog_add("LogBerry Logger stopped.")
tg.send("User interrupted program execution - Logger stopped.")
glog_close()