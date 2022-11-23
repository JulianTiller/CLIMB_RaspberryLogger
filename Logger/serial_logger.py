import time
import serial 
from datetime import datetime
import csv
from glog import glog_add
from glog import tss

power_cycle_triggered = 0
serlog_data = " "
wdt_timeout = (60*15) # seconds till LogBerry power cycles OBC

def request_powercycle():
    global power_cycle_triggered
    return power_cycle_triggered
    
def powercycle_done():
    global power_cycle_triggered
    global ts_wdt_feed
    power_cycle_triggered = 0
    ts_wdt_feed = datetime.now() # Reset watchdog timeout

def serlog_stop():
    global run
    glog_add("Serial logger stop routine triggered")
    run = 0

def serlog_read_keepalive():
    return keepalive

def serdata_parse(data):
    global power_cycle_triggered
    global serlog_data
    global ts_wdt_feed
    try:
        if(serlog_data.find('Supervision watchdog feed') != -1):
            glog_add('Supervision watchdog reset')
            ts_wdt_feed = datetime.now() # Watchdog on LogBerry is feed by the OBC
            power_cycle_triggered = 0
    except:
        glog_add('Serial parsing failed')

def wdt_handle():
    global power_cycle_triggered
    global serlog_data
    global ts_wdt_feed
    if(((datetime.now() - ts_wdt_feed).total_seconds() > wdt_timeout) and (power_cycle_triggered == 0)):
        # LogBerry WDT was not reset for more than wdt_timeout seconds -> force power cycle of OBC
        power_cycle_triggered = 1
        ts_wdt_feed = datetime.now()
        glog_add("LogBerry watchdog timeput: Forcing OBC reset.")
        # Wait for main logger module to powercycle OBC and clear power_cycle_triggered flag
        
def serial_logger_worker():        
    global serlog_data
    global keepalive
    global ts_wdt_feed
    global run
    global power_cycle_triggered
        
    keepalive = 0
    run = 1
    counter = 0
    ts_wdt_feed = datetime.now()
    power_cycle_triggered = 0
    
    glog_add("Serial logger startup")
    
    # Init serial logfile     
    # ////  open a .csv > make it as a dictionary to write in > write headers > clear everything ====> serial log file is initializd
    ts = datetime.now()    
    serlog_filename = '/home/pi/logger/logs/serlog/serial_log_' + ts.strftime("%d%m%Y_%H%M%S") + '.csv'
    glog_add("Using: " + serlog_filename)
    serlog_file = open(serlog_filename, 'a', newline='') # , newline=''
    fieldnames = ['Timestamp','Message']
    serlog_writer = csv.DictWriter(serlog_file, fieldnames=fieldnames)
    serlog_writer.writeheader() # Init new logfile
    serlog_file.flush()
    
    # Init serial interface 

    # //// setting the port COM14 as serial port

    try:
        ser = serial.Serial(  
            port='/dev/ttyAMA0',
            #port='COM14',
            baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
            )
    except:
        glog_add("Unable to open serial port.")
        quit()

    glog_add("Opened serial port " + ser.name)
    glog_add("Serial logging running.")
    


    while run:      #///////// run is 1 means true so start the while until the run becomes false
        keepalive = keepalive + 1 # Increase counter regularly
        #ser.write(str.encode("test " + str(counter) + "\n")) # debug only
        #counter = counter + 1 # debug only
        
        ser_rec_chars = ser.inWaiting()
        if ser_rec_chars > 0:    #///////// Read from serial port
            try:
                serlog_data = serlog_data + ser.read(ser_rec_chars).decode('utf-8')
            except:
                glog_add("Reading from serial port failed.")
                serlog_data = ''
                #run = 0
                
            while True:
                le = serlog_data.find('\n')
                if(le != -1):
                    # Line found
                    line = serlog_data[0:le];
                    serdata_parse(line)
                    line = "{{" + line + "}}" # Wrap received message
                    
                    #print(line)
                    try:
                        serlog_writer.writerow({'Timestamp': tss(), 'Message': line})
                    except:
                        glog_add("Writing to serial log failed.")
                        run = 0
                        break
                    serlog_data = serlog_data[le+1:] # Crop remaining serlog_data
                else:
                    # No further lines found
                    break            
            serlog_file.flush() # Write data to disk
        else:            
            time.sleep(0.25)
            
        wdt_handle()    

    glog_add("Serial logger stopped")
    ser.close()
    try:
        serlog_file.close()
    except:
        glog_add('Error closing perlog')
    
