import time
import serial 
from datetime import datetime
import csv
from glog import tss

def rs485_worker():
    # Init serial logfile
    ts = datetime.now()    
    rs485log_filename = '/home/pi/logger/logs/rs485/log_' + ts.strftime("%d%m%Y_%H%M%S") + '.csv'
    print("Using: " + rs485log_filename)
    rs485log_file = open(rs485log_filename, 'a', newline='') # , newline=''
    fieldnames = ['Timestamp','Message']
    rs485log_writer = csv.DictWriter(rs485log_file, fieldnames=fieldnames)
    rs485log_writer.writeheader() # Init new logfile
    rs485log_file.flush()

    try:
        ser = serial.Serial(  
            port='/dev/ttyUSB0',
            baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
    except:
        print("Unable to open serial port.")
        quit()

    print("Opened serial port " + ser.name)
    print("Serial logging running.")

    while 1:
             
        ser_rec_chars = ser.inWaiting()
        if ser_rec_chars > 0:
            try:
                rs485log_data = rs485log_data + ser.read(ser_rec_chars).decode('utf-8')
            except:
                print("Reading from serial port failed.")
                rs485log_data = ''
               
            while True:
                le = rs485log_data.find('\n')
                if(le != -1):
                    # Line found
                    line = rs485log_data[0:le];
                    print(tss() + ': ' +line)
                    try:
                        rs485log_writer.writerow({'Timestamp': tss(), 'Message': line})
                        rs485log_file.flush()
                    except:
                        print("Writing to serial log failed.")
                        run = 0
                        break
                    rs485log_data = rs485log_data[le+1:] # Crop remaining
                else:
                    # No further lines found
                    break
        else:            
            time.sleep(1)            
                    
    print("RS485 logger stopped")
    ser.close()
    try:
        rs485log_file.close()
    except:
        print('Error closing rs485 log')
        
if __name__ == '__main__':
    rs485_worker()        
