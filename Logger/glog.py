from datetime import datetime
import csv

print_messages = 1

def tss():
	ts = datetime.now()	
	return ts.strftime("%d.%m.%Y %H:%M:%S.%f")#[:-1]
	
def glog_init(glog_filename):
	# Init global logfile
	global glog_writer
	global glog_file
	
	glog_file = open(glog_filename, 'a', newline='') #
	fieldnames = ['Timestamp','Message']
	glog_writer = csv.DictWriter(glog_file, fieldnames=fieldnames)
	glog_add(" ")
	glog_add("-------------------------------------------------------")
	glog_add("LogBerry logger starting...")
	glog_add("LogBerry global logger started.")

def glog_flush():
	glog_file.flush()

def glog_add(message):
    try:
        glog_writer.writerow({'Timestamp': tss(), 'Message': " " + message})
        glog_file.flush()
        if print_messages:
            print(tss()[:-3] + ", " + message)
    except:
        print('Error writing glog')
	
def glog_close():
	glog_file.flush()
	glog_file.close()

