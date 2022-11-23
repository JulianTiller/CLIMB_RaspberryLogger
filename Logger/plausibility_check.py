



def plausibility_check(m_3v3a_volt,m_3v3c_volt,m_3v3a_cur ,m_3v3c_cur,m_rtc_bat_volt,m_18v_volt ,m_5v_volt ,m_vee_volt,m_vcc_disable_volt,m_obc_reset_volt , m_spd_volt ,m_spc_volt,m_spb_volt, m_spa_volt,m_3v3_up_volt, m_controller_volt):
    cerr = 0
    print('\n----------------------------------------------')
    print('Executing plausibility check...')
    
    if(m_3v3a_volt < 3.1 or m_3v3a_volt > 3.4):
        print('---> 3V3-A Voltage out of range')
        cerr = cerr + 1
        
    if(m_3v3c_volt < 3.1 or m_3v3a_volt > 3.4):
        print('3---> V3-A Voltage out of range')
        cerr = cerr + 1
    
    if(m_3v3_up_volt < 3.0 or m_3v3a_volt > 3.4):
        print('---> Selected OBC input voltage (UP) out of range')
        cerr = cerr + 1    
        
    if(m_controller_volt < 3.0 or m_3v3a_volt > 3.4):
        print('---> Main controller supply voltage out of range')
        cerr = cerr + 1
        
    if(m_rtc_bat_volt < 2.8 or m_3v3a_volt > 3.6):
        print('---> RTC backup voltage out of range')
        cerr = cerr + 1
        
    if(m_3v3a_cur > 0.15):
        print('---> 3V3-A current too high')
        cerr = cerr + 1
        
    if(m_3v3c_cur > 0.15):
        print('---> 3V3-C current too high')
        cerr = cerr + 1
        
    if((m_3v3a_cur + m_3v3c_cur) < 0.05):
        print('---> OBC supply current seems too low')
        cerr = cerr + 1
        
    if(m_3v3a_cur > 0.03 and m_3v3c_cur > 0.03):
        print('---> OBC supply current distribution is odd')
        cerr = cerr + 1
        
    if(m_spa_volt < 3.0 or m_spa_volt > 3.4):
        print('---> 3V3-SP-A not within limits')
        cerr = cerr + 1
        
    if(m_spb_volt < 3.0 or m_spb_volt > 3.4):
        print('---> 3V3-SP-B not within limits')
        cerr = cerr + 1
        
    if(m_spc_volt < 3.0 or m_spc_volt > 3.4):
        print('---> 3V3-SP-C not within limits')
        cerr = cerr + 1
        
    if(m_spd_volt < 3.0 or m_spd_volt > 3.4):
        print('---> 3V3-SP-D not within limits')
        cerr = cerr + 1
        
    if(m_obc_reset_volt < 3.0 or m_obc_reset_volt > 3.4):
        print('---> OBC reset pin voltage not within limits')
        cerr = cerr + 1
        
    if(m_vcc_disable_volt > 0.1):
        print('---> OBC VCC disable pin is high')
        cerr = cerr + 1    
        
    if(m_18v_volt < 17.5 or m_18v_volt > 21.5):
        print('---> 18 V supply not within limits')
        cerr = cerr + 1
    
    if(m_5v_volt < 4.7 or m_5v_volt > 5.3):
        print('---> 5 V supply not within limits')
        cerr = cerr + 1    
        
    if(m_vee_volt < 3.0 or m_vee_volt > 3.4):
        print('---> VEE (dosimeter) supply not within limits')
        cerr = cerr + 1 

    print('Errors: ' + str(cerr))

    if(cerr > 0):
        print('Plausibility check failed!')
    else:
        print('Plausibility check passed. :)')
    
    print('----------------------------------------------\n')
    return cerr    
       
    
        
        
        
        
        
        
    