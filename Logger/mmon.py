from mcp3208 import MCP3208
import time
import RPi.GPIO as GPIO
from datetime import datetime
import csv
import os.path
from glog import tss
import socket
from plausibility_check import plausibility_check

import sys



dT = 0.5 # seconds




def c3v3a_to_current(volt):    
    return ((volt / 0.1 / 50.0) * C3V3A_CUR_GAIN + C3V3A_CUR_OFFSET)
    
def c3v3c_to_current(volt):
    return ((volt / 0.1 / 50.0) * C3V3C_CUR_GAIN + C3V3C_CUR_OFFSET)



def mmon_worker():
    global C3V3A_CUR_GAIN
    global C3V3A_CUR_OFFSET
    global C3V3C_CUR_GAIN
    global C3V3C_CUR_OFFSET
    global power_cycle_triggered
    global run
    global print_raw_data
    global print_data
    
    print_data = 1
    print_raw_data = 0
    do_plausibility_check = 1
    

    if(len(sys.argv) == 2):
        if(sys.argv[1] == 'r'):
            print_raw_data = 1
            print_data = 0
            do_plausibility_check = 0
        elif(sys.argv[1] == 'p'):
            do_plausibility_check = 1
            print_data = 0
            print_raw_data = 0
        elif(sys.argv[1] == 'd'):
            do_plausibility_check = 0
            print_data = 1
            print_raw_data = 0
        
    run = 1
    counter = 0
    print("M-Monitor start")
    
    logberry_name = socket.gethostname() # "LogBerry0e" "LogBerry1" "LogBerry2"

    if(logberry_name == 'LogBerry0e'):
        print('Using calibration for ' + logberry_name)
        C3V3A_CUR_GAIN = 0.5
        C3V3A_CUR_OFFSET = -0.0075
        C3V3C_CUR_GAIN = 0.5
        C3V3C_CUR_OFFSET = -0.000
    elif(logberry_name == 'LogBerry1'):
        # verified
        print('Using calibration for ' + logberry_name)
        C3V3A_CUR_GAIN = 1.0
        C3V3A_CUR_OFFSET = -0.0021
        C3V3C_CUR_GAIN = 1.0
        C3V3C_CUR_OFFSET = -0.0021
    elif(logberry_name == 'LogBerry2'):
        print('Using calibration for ' + logberry_name)
        C3V3A_CUR_GAIN = 1.0
        C3V3A_CUR_OFFSET = -0.00322
        C3V3C_CUR_GAIN = 1.0
        C3V3C_CUR_OFFSET = -0.00226
    else:
        print('Using default calibration')
        C3V3A_CUR_GAIN = 1.0
        C3V3A_CUR_OFFSET = -0.002
        C3V3C_CUR_GAIN = 1.0
        C3V3C_CUR_OFFSET = -0.002
        
    start = datetime.now()

    ai1 = MCP3208(0,0)
    ai2 = MCP3208(0,1)
    ai3 = MCP3208(1,0)

   
    time.sleep(1)
    
    while run:                

        m_3v3a_volt     = ai3.readf(1)
        m_3v3c_volt     = ai3.readf(0)
        m_3v3a_cur      = c3v3a_to_current(ai3.readf(5))
        m_3v3c_cur      = c3v3c_to_current(ai3.readf(4))
        #m_rtc_bat_volt  = ai3.readf(2);
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
         
        if(do_plausibility_check):
            plausibility_check(m_3v3a_volt,m_3v3c_volt,m_3v3a_cur ,m_3v3c_cur,m_rtc_bat_volt,m_18v_volt ,m_5v_volt ,m_vee_volt,m_vcc_disable_volt,m_obc_reset_volt , m_spd_volt ,m_spc_volt,m_spb_volt, m_spa_volt,m_3v3_up_volt, m_controller_volt)
 
       
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

        time.sleep(dT-0.0027)

        
        
    print("M-Monitor stopped")

if __name__ == '__main__':
    mmon_worker()