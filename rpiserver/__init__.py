import json
import os
from flask import Flask
import requests
import RPi.GPIO as GPIO

######################
# Variables
######################

# GPIOs: Reverse logic here for relay because of 3.3V difference
GPIO_on = GPIO.LOW # =False
GPIO_off = GPIO.HIGH # =True


######################
# Functions
######################

# Load data from json
def load_data(file_path):
    f = open(file_path)
    loaded = json.load(f)
    f.close()
    return loaded


def write_data(file_path, to_write):
    with open(file_path, 'w') as f2:
        json.dump(to_write, f2, indent=4)


def initiate_pin_states(pins_in):
    GPIO.setmode(GPIO.BOARD)

    for key in pins_in:
        # Check if device output is an actual pin or IP
        if isinstance(pins_in[key]['pin'], int):
            GPIO.setup(pins_in[key]['pin'], GPIO.OUT)


def read_ip_state(ip):
    r = requests.post("http://" + ip)
    r_str = str(r.content)
    state = r_str.split('<br>')[0].split('now: ')[1]
    if state == 'ON':
        return GPIO_on
    if state == 'OFF':
        return GPIO_off


def read_pin_states(pins_in):
    for key in pins_in:
        if isinstance(pins_in[key]['pin'], int):
            pins_in[key]['state'] = GPIO.input(pins_in[key]['pin'])
        elif isinstance(pins_in[key]['pin'], str):
            pins_in[key]['state'] = read_ip_state(pins_in[key]['pin'])
    return pins_in


# Initiate variables for server start
path = os.path.dirname(os.path.abspath(__file__))
path_json = os.path.join(path, '..', 'schedule.json')


######################
# Initialise app
######################

# Flask initialisation
app = Flask(__name__)

# activate/make views ready
import rpiserver.views

# GPIO housekeeping
# GPIO.cleanup()
