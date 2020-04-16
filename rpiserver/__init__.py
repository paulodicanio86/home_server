import json
import os
from flask import Flask
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


def initiate_pin_states(file_path):
    pins_in = load_data(file_path)
    for key in pins_in:
        GPIO.setup(pins_in[key]['pin'], GPIO.OUT)


def read_pin_states(pins_in):
    for key in pins_in:
        pins_in[key]['state'] = GPIO.input(pins_in[key]['pin'])
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
