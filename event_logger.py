#!/usr/bin/python
import RPi.GPIO as GPIO # sudo pip install RPi.GPIO
import time
from datetime import datetime
from glog import tss
from glog import glog_add
import csv

print_events = 1

#http://www.netzmafia.de/skripten/hardware/RasPi/RasPi_GPIO_int.html

GPIO.setwarnings(False) 

# Pin assignment
'''
PIN_Watchdog_Feed    =    29    # GP05
PIN_VCC_Fault        =    31    # GP06
PIN_RESET_OUT        =    33    # GP13
PIN_Floga_Fault        =    11    # GP17
PIN_WDT_OUT            =    15    # GP22, Output of EWDT
PIN_THRUSTER_CS_P    =    16    # GP23
PIN_BL_SEL1            =    18    # GP24
PIN_STACIE_A_IO1_P    =    37    # GP26
'''

PIN_Watchdog_Feed    =    5    # GP05
PIN_VCC_Fault        =    6    # GP06
PIN_RESET_OUT        =    13    # GP13
PIN_Floga_Fault        =    17    # GP17
PIN_WDT_OUT            =    22    # GP22, Output of EWDT
PIN_THRUSTER_CS_P    =    23    # GP23
PIN_BL_SEL1            =    24    # GP24
PIN_STACIE_A_IO1_P    =    26    # GP26

def eventlog_add(event):
    try:
        eventlog_writer.writerow({'Timestamp': tss(), 'Event': event})
        eventlog_file.flush()
    except:
        glog_add('Error writing to eventlog')

def eventlog_stop():
    global run
    glog_add("Event logger stop routine triggered")
    run = 0

def eventlog_read_keepalive():
    return keepalive
    
def get_resets():
    global reset_counter
    return reset_counter

# Callback functions
def int_event_wdt_feed(channel):
    #if GPIO.input(PIN_Watchdog_Feed) == 0:      
        # Falling edge detected
        #event_val = "0f_WDT_Feed_Falling"
    #else:   
        # Rising edge detected
    event_val = "0r_WDT_Feed_Rising"
    eventlog_add(event_val)  
    if print_events:
        print (tss() + ": " + event_val)
        
def int_event_vcc_fault(channel):
    if GPIO.input(PIN_VCC_Fault) == 0:      
        # Falling edge detected
        event_val = "1f_VCC_fault_Falling"
    else:   
        # Rising edge detected
        event_val = "1r_VCC_fault_Rising"
    eventlog_add(event_val)  
    if print_events:
        print (tss() + ": " + event_val)

def int_event_wdt_out(channel):
    if GPIO.input(PIN_WDT_OUT) == 0:      
        # Falling edge detected
        event_val = "2f_WDT_OUT_Falling"
    else:   
        # Rising edge detected
        event_val = "2r_WDT_OUT_Rising"
    eventlog_add(event_val)  
    if print_events:
        print (tss() + ": " + event_val)

def int_event_floga_fault(channel):
    if GPIO.input(PIN_Floga_Fault) == 0:      
        # Falling edge detected
        event_val = "3f_FLOGA_fault_Falling"
    else:   
        # Rising edge detected
        event_val = "3r_FLOGA_fault_Rising"
    eventlog_add(event_val)  
    if print_events:
        print (tss() + ": " + event_val)
  
def int_event_thruster_cs(channel):
    if GPIO.input(PIN_THRUSTER_CS_P) == 0:      
        # Falling edge detected
        event_val = "4f_thruster_cs_Falling"
    else:   
        # Rising edge detected
        event_val = "4r_thruster_cs_Rising"
    eventlog_add(event_val)  
    if print_events:
        print (tss() + ": " + event_val) 
        
def int_event_bl_sel(channel):
    if GPIO.input(PIN_BL_SEL1) == 0:      
        # Falling edge detected
        event_val = "5f_bl_sel_Falling"
    else:   
        # Rising edge detected
        event_val = "6r_bl_sel_Rising"
    eventlog_add(event_val)  
    if print_events:
        print (tss() + ": " + event_val)  
        
def int_event_stacie_a_io1(channel):
    if GPIO.input(PIN_STACIE_A_IO1_P) == 0:      
        # Falling edge detected
        event_val = "7f_stacie_a_io1_Falling"
    else:   
        # Rising edge detected
        event_val = "7r_stacie_a_io1_Rising"
    eventlog_add(event_val)  
    if print_events:
        print (tss() + ": " + event_val) 

def int_event_reset_out(channel):
    global reset_counter
    if GPIO.input(PIN_RESET_OUT) == 0:      
        # Falling edge detected
        event_val = "8f_RESET_out_Falling"
    else:   
        # Rising edge detected
        event_val = "8r_RESET_out_Rising"
        reset_counter = reset_counter + 1  
        glog_add("OBC-Reset detected; " + str(reset_counter))
        
    eventlog_add(event_val)  
    
    if print_events:
        print (tss() + ": " + event_val)    

def event_logger_worker():
    global keepalive
    global run
    global reset_counter
    keepalive = 0
    run = 1
    reset_counter = 0
    
    glog_add("Starting event logger thread")

    # Init serial logfile
    global eventlog_writer    
    global eventlog_file    
    ts = datetime.now()    
    eventlog_filename = '/home/pi/logger/logs/events/event_log_' + ts.strftime("%d%m%Y_%H%M%S") + '.csv'
    glog_add("Using: " + eventlog_filename)
    eventlog_file = open(eventlog_filename, 'a', newline='') # , newline=''
    fieldnames = ['Timestamp','Event']
    eventlog_writer = csv.DictWriter(eventlog_file, fieldnames=fieldnames)
    eventlog_writer.writeheader() 

    GPIO.setmode(GPIO.BCM)
    #GPIO.setmode(GPIO.BOARD)



    # Pin initialization

    GPIO.setup(PIN_VCC_Fault,         GPIO.IN)#, pull_up_down = GPIO.PUD_UP) 
    GPIO.setup(PIN_RESET_OUT,         GPIO.IN)#, pull_up_down = GPIO.PUD_UP) 
    GPIO.setup(PIN_Floga_Fault,     GPIO.IN)#, pull_up_down = GPIO.PUD_UP) 
    GPIO.setup(PIN_WDT_OUT,         GPIO.IN)#, pull_up_down = GPIO.PUD_UP) 
    GPIO.setup(PIN_THRUSTER_CS_P,     GPIO.IN, pull_up_down = GPIO.PUD_UP) 
    GPIO.setup(PIN_BL_SEL1,         GPIO.IN)#, pull_up_down = GPIO.PUD_UP) 
    GPIO.setup(PIN_STACIE_A_IO1_P,     GPIO.IN)#, pull_up_down = GPIO.PUD_UP)
    GPIO.setup(PIN_Watchdog_Feed,     GPIO.IN)#, pull_up_down = GPIO.PUD_UP) # , pull_up_down = GPIO.PUD_UP

    debounce_time = 2

    # Add interrupt events
    GPIO.add_event_detect(PIN_Watchdog_Feed,      GPIO.RISING,     callback = int_event_wdt_feed,         bouncetime = debounce_time)  
    GPIO.add_event_detect(PIN_VCC_Fault,          GPIO.BOTH,     callback = int_event_vcc_fault,     bouncetime = debounce_time)  
    GPIO.add_event_detect(PIN_RESET_OUT,          GPIO.BOTH,     callback = int_event_reset_out,     bouncetime = debounce_time)  
    GPIO.add_event_detect(PIN_Floga_Fault,          GPIO.BOTH,     callback = int_event_floga_fault,     bouncetime = debounce_time)  
    GPIO.add_event_detect(PIN_WDT_OUT,              GPIO.BOTH,     callback = int_event_wdt_out,         bouncetime = debounce_time)  
    GPIO.add_event_detect(PIN_THRUSTER_CS_P,      GPIO.BOTH,     callback = int_event_thruster_cs,     bouncetime = debounce_time)  
    GPIO.add_event_detect(PIN_BL_SEL1,              GPIO.BOTH,     callback = int_event_bl_sel,         bouncetime = debounce_time) 
    GPIO.add_event_detect(PIN_STACIE_A_IO1_P,      GPIO.BOTH,     callback = int_event_stacie_a_io1,     bouncetime = debounce_time)  

    glog_add("Event logger running")
    eventlog_file.flush()
    
    eventlog_add("Initialized")

    while run:
        keepalive = keepalive + 1 # Increase counter regularly
        time.sleep(0.5)

    glog_add("Event logger stopped unexpectedly")
    GPIO.cleanup()
    eventlog_file.close()
    
def eventlog_stop():
    glog_add("Event logger stopped")    
    GPIO.cleanup()
    try:
        eventlog_file.close()
    except:
        glog_add('Error closing perlog')