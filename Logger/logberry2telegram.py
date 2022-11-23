import telegram_send
# 946802707:AAEZeNAWElevxE2iPx6EDQXs5wIPlB7smCI
# https://telegram.me/LogBerry1_bot
# pw 08411

# global: 1056147475:AAFco_gNC69tOwVLa9-8xzB_7sjP0TBBP-M
# t.me/LogBerryBot
# sudo telegram-send -g --configure
# pw 04857

class logberry2telegram(object):
    def __init__(self, logberry_name, enabled):
        self.logberry_name = logberry_name
        self.enabled = enabled
        
    def send(self, message):
        if(self.enabled):
            try:
                data = self.logberry_name + ": " + message
                telegram_send.send(messages=[data],conf='/etc/telegram-send.conf')
            except:
                print('Error sending telegram message')
        