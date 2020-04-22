import json, os
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO_on = GPIO.LOW # =False
GPIO_off = GPIO.HIGH # =True


# Load data from json
def load_data(file_path):
    f = open(file_path)
    loaded = json.load(f)
    f.close()
    return loaded


def write_data(file_path, to_write):
    with open(file_path, 'w') as f2:
        json.dump(to_write, f2, indent=4)


now = datetime.now()
hour = now.strftime("%H")
minute = now.strftime("%M")

path = os.path.dirname(os.path.abspath(__file__))
path_json = os.path.join(path, 'schedule.json')
data = load_data(path_json)


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

                # capture last_on time
                now_str = now.strftime("%d/%m/%Y, %H:%M:%S")
                data[entry]['last_on'] = now_str
                write_data(path_json, data)
