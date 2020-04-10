import json
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO_on = GPIO.LOW # =False
GPIO_off = GPIO.HIGH # =True


now = datetime.now()
hour = now.strftime("%H")
minute = now.strftime("%M")

# hour = '12'
# minute = '30'

f = open('/home/pi/home_server/schedule.json')
data = json.load(f)

for entry in data:
    data_dic = data[entry]

    if data_dic['mode'] == 'on_off':
        for on_time in data_dic['on']:
            if on_time.split(':')[0] == hour and on_time.split(':')[1] == minute:
                GPIO.setup(data_dic['pin'], GPIO.OUT)
                GPIO.output(data_dic['pin'], GPIO_on)

        for off_time in data_dic['off']:
            if off_time.split(':')[0] == hour and off_time.split(':')[1] == minute:
                GPIO.setup(data_dic['pin'], GPIO.OUT)
                GPIO.output(data_dic['pin'], GPIO_off)

    elif data_dic['mode'] == 'duration':
        for on_time in data_dic['on']:
            if on_time.split(':')[0] == hour and on_time.split(':')[1] == minute:

                GPIO.setup(data_dic['pin'], GPIO.OUT)
                GPIO.output(data_dic['pin'], GPIO_on)
                sleep(data_dic['duration'])
                GPIO.output(data_dic['pin'], GPIO_off)




