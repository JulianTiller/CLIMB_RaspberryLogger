from mcp3208 import MCP3208
import time
import RPi.GPIO as GPIO
from datetime import datetime
import csv
import os.path
import socket
from glog import tss
from glog import glog_add
from plausibility_check import plausibility_check

perlog_filename = 'periodic_log.csv'
print_data = 0
print_raw_data = 0
dT = 0.1 # seconds

def perlog_stop():
    global run
    glog_add("Periodic logger stop routine triggered")
    run = 0
    
def get_snapshot():
    global snapshot_string
    return snapshot_string
       

def perlog_read_keepalive():
    return keepalive

def c3v3a_to_current(volt):
    global C3V3A_CUR_GAIN
    global C3V3A_CUR_OFFSET
    return ((volt / 0.1 / 50.0) * C3V3A_CUR_GAIN + C3V3A_CUR_OFFSET)
    
def c3v3c_to_current(volt):
    global C3V3C_CUR_GAIN
    global C3V3C_CUR_OFFSET
    return ((volt / 0.1 / 50.0) * C3V3C_CUR_GAIN + C3V3C_CUR_OFFSET)



def periodic_logger_worker():
    global power_cycle_triggered
    global run
    global keepalive
    global C3V3A_CUR_GAIN
    global C3V3A_CUR_OFFSET
    global C3V3C_CUR_GAIN
    global C3V3C_CUR_OFFSET
    global snapshot_string
    
    snapshot_string = ""    
    keepalive = 0
    run = 1
    counter = 0
    pcd = 20
    
    power_cycle_triggered = 0
    glog_add("Periodic logger starting")

    logberry_name = socket.gethostname() # "LogBerry0e" "LogBerry1" "LogBerry2"

    if(logberry_name == 'LogBerry0e'):
        glog_add('Using calibration for LogBerry0e')
        C3V3A_CUR_GAIN = 0.5
        C3V3A_CUR_OFFSET = -0.0075
        C3V3C_CUR_GAIN = 0.5
        C3V3C_CUR_OFFSET = -0.000
    elif(logberry_name == 'LogBerry1'):
        # verified
        glog_add('Using calibration for LogBerry1')
        C3V3A_CUR_GAIN = 1.0
        C3V3A_CUR_OFFSET = -0.0021
        C3V3C_CUR_GAIN = 1.0
        C3V3C_CUR_OFFSET = -0.0021
    elif(logberry_name == 'LogBerry2'):
        glog_add('Using calibration for LogBerry2')
        C3V3A_CUR_GAIN = 1.0
        C3V3A_CUR_OFFSET = -0.00322
        C3V3C_CUR_GAIN = 1.0
        C3V3C_CUR_OFFSET = -0.00226
    else:
        glog_add('Using default calibration')
        C3V3A_CUR_GAIN = 1.0
        C3V3A_CUR_OFFSET = -0.002
        C3V3C_CUR_GAIN = 1.0
        C3V3C_CUR_OFFSET = -0.002

#    if os.path.isfile(perlog_filename):
#        perlog_newfile = 0;
#    else:
#        perlog_newfile = 1;

#    csvfile = open("logs/" + perlog_filename, 'a', newline='') #, newline=''

# Init periodic logfile
    ts = datetime.now()    
    perlog_filename = '/home/pi/logger/logs/periodic/periodic_log_' + ts.strftime("%d%m%Y_%H%M%S") + '.csv'
    glog_add("Using periodic logfile: " + perlog_filename)
    perlog_file = open(perlog_filename, 'a', newline='') # , newline=''

    fieldnames = ['Timestamp',\
    '3V3_A_Voltage', '3V3_C_Voltage',\
    '3V3_A_Current','3V3_C_Current',\
    '18V_Voltage','5V_Voltage',\
    'VEE_Voltage','Reference_Voltage',\
    'VCC_Disable_Voltage','OBC_Reset_Voltage',\
    '3V3_SP_A_Voltage','3V3_SP_B_Voltage',\
    '3V3_SP_C_Voltage','3V3_SP_D_Voltage',\
    '3V3_Controller_Voltage','RTC_BAT_Voltage']
    writer = csv.DictWriter(perlog_file, fieldnames=fieldnames)
    writer.writeheader() # Init new logfile
    perlog_file.flush()
        

    start = datetime.now()

    ai1 = MCP3208(0,0)
    ai2 = MCP3208(0,1)
    ai3 = MCP3208(1,0)
    glog_add("ADCs initialized.")    

    start = datetime.now()
    glog_add("Periodic logger running")
    
    time.sleep(1)
    
    while run:                
        keepalive = keepalive + 1 # Increase counter regularly    
        
        m_3v3a_volt     = ai3.readf(1)
        m_3v3c_volt     = ai3.readf(0)
        m_3v3a_cur      = c3v3a_to_current(ai3.readf(5))
        m_3v3c_cur      = c3v3c_to_current(ai3.readf(4))
        #m_rtc_bat_volt  = ai3.readf(2); # hiz-1
        #m_hiz2_volt     = ai3.readf(3);
        #m_ext6_volt     = ai3.readf(6);
        m_rtc_bat_volt     = ai1.readf(7);

        m_18v_volt      =      6.666*ai1.readf(0) # voltage divider 680k/120k
        m_5v_volt       =      2*ai1.readf(1) # voltage divider 10k/10k
        m_vee_volt      =      ai1.readf(2)
        
        m_vcc_disable_volt     =     ai2.readf(0)
        m_obc_reset_volt       =     ai2.readf(1)
        m_spd_volt             =     ai2.readf(2)
        m_spc_volt             =     ai2.readf(3)
        m_spb_volt             =     ai2.readf(4)
        m_spa_volt             =     ai2.readf(5)
        m_3v3_up_volt          =     ai2.readf(6)        
        m_controller_volt      =     ai2.readf(7)
        
        snapshot_string = "3V3-A: {:.2f}".format(m_3v3a_volt) + ' V, '+ "{:.2f}".format(m_3v3a_cur*1000)+ ' mA\n'                         \
                        + "3v3-C: {:.2f}".format(m_3v3c_volt) + ' V, '+ "{:.2f}".format(m_3v3c_cur*1000) + ' mA\n'                 \
                        + "RTC: {:.2f}".format(m_rtc_bat_volt) + ' V\n' + "18V: {:.2f}".format(m_18v_volt)  + ' V, '          \
                        + "5V: {:.2f}".format(m_5v_volt) + ' V, ' + "VEE: {:.2f}".format(m_vee_volt) + ' V\n'                   \
                        + "Vup: {:.2f}".format(m_3v3_up_volt) + ' V, ' + "VMCU: {:.2f}".format(m_controller_volt) + ' V'
                
        try:        
            writer.writerow({'Timestamp': tss(),\
                '3V3_A_Current': m_3v3a_cur, '3V3_C_Current': m_3v3c_cur,\
                '3V3_A_Voltage': m_3v3a_volt, '3V3_C_Voltage': m_3v3c_volt,\
                '18V_Voltage': m_18v_volt, '5V_Voltage':m_5v_volt,\
                'VEE_Voltage': m_vee_volt,'Reference_Voltage': m_3v3_up_volt,\
                'VCC_Disable_Voltage': m_vcc_disable_volt,'OBC_Reset_Voltage': m_obc_reset_volt,\
                '3V3_SP_A_Voltage': m_spa_volt,'3V3_SP_B_Voltage': m_spb_volt,\
                '3V3_SP_C_Voltage': m_spc_volt,'3V3_SP_D_Voltage': m_spd_volt,\
                '3V3_Controller_Voltage':m_controller_volt,'RTC_BAT_Voltage':m_rtc_bat_volt})
            perlog_file.flush()
        except:
            glog_add('Error writing to perlog')

        if print_raw_data:
            print('\n' + tss())
            print("AI1:");
            for i in range(8):
                print('  ADC[{}]: {:.2f}'.format(i, ai1.readf(i)))
            print("AI2:");
            for i in range(8):
                print('  ADC[{}]: {:.2f}'.format(i, ai2.readf(i)))
            print("AI3:");
            for i in range(8):
                print('  ADC[{}]: {:.2f}'.format(i, ai3.readf(i)))

        if print_data:
            print("\n" + tss())
            print("3V3-A: %.2f V, %.2f mA" % (m_3v3a_volt, (m_3v3a_cur)*1000))
            print("3V3-C: %.2f V, %.2f mA" % (m_3v3c_volt, (m_3v3c_cur)*1000))
            print("3V3-UP: %.2f V, VCC-MCU %.2f V" % (m_3v3_up_volt,m_controller_volt))
            print("Vbackup: %.2f V, 5V: %.2f V, 18V: %.2f V, VEE: %.2f V" % (m_rtc_bat_volt, m_5v_volt, m_18v_volt, m_vee_volt))
            print("SP-A: %.2f V, SP-B: %.2f V, SP-C: %.2f V, SP-D: %.2f V" % (m_spa_volt,m_spb_volt,m_spc_volt,m_spd_volt))
            print("Reset: %.2f V, VCC-DIS %.2f V" % (m_obc_reset_volt,m_vcc_disable_volt))

        
        if pcd == 0:
            cerr = plausibility_check(m_3v3a_volt,m_3v3c_volt,m_3v3a_cur ,m_3v3c_cur,m_rtc_bat_volt,m_18v_volt ,m_5v_volt ,m_vee_volt,m_vcc_disable_volt,m_obc_reset_volt , m_spd_volt ,m_spc_volt,m_spb_volt, m_spa_volt,m_3v3_up_volt, m_controller_volt)
            glog_add('Plausibility check found ' + str(cerr) + ' errors')
            pcd = -1
        elif pcd > 0:        
            pcd = pcd - 1
            
        time.sleep(dT-0.0027)

        
        
    glog_add("Periodic logger stopped unexpectedly")
    try:
        perlog_file.close()
    except:
        glog_add('Error closing perlog')
