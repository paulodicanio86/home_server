import json
import os
from flask import Flask
import requests
import RPi.GPIO as GPIO

######################
# Variables
######################

# GPIOs: Reverse logic here for relay because of 3.3V difference
GPIO_on = GPIO.LOW  # =False
GPIO_off = GPIO.HIGH  # =True


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


def initiate_gpio_states(pins_in):
    GPIO.setmode(GPIO.BOARD)

    #for key in pins_in:
        # Check if device output is an actual pin or IP
        # If a pin, define it as an output GPIO
     #   if isinstance(pins_in[key]['pin'], int):
      #      GPIO.setup(pins_in[key]['pin'], GPIO.OUT)    ### TAKE THIS ENTIRE BLOCK OUT?


def read_ip_state(ip):
    return False
    ## AS SAFETY STOP HERE FOR NOW
    r = requests.post("http://" + ip)  ## This needs fixing. TO MANY RETRIES?
    r_str = str(r.content)
    state = r_str.split('<br>')[0].split('now: ')[1]
    if state == 'ON':
        return True
    if state == 'OFF':
        return False


def read_gpio_state(pin):
    return GPIO.input(pin)


def read_pin_states(pins_in):
    for key in pins_in:
        if isinstance(pins_in[key]['pin'], int):
            pins_in[key]['state'] = read_gpio_state(pins_in[key]['pin'])
        elif isinstance(pins_in[key]['pin'], str):
            pins_in[key]['state'] = read_ip_state(pins_in[key]['pin'])
    return pins_in


def turn_gpio(pin, state):
    GPIO.setup(pin, GPIO.OUT)
    if state == 'ON':
        GPIO.output(pin, GPIO_on)
    elif state == 'OFF':
        GPIO.output(pin, GPIO_off)


def turn_ip(ip, state):
    # state should either be "ON" or "OFF"
    requests.post("http://" + ip + "/RELAY=" +state)


def turn_device(pin, state):
    # If pin is an integer the GPIO is used
    if isinstance(pin, int):
        turn_gpio(pin, state)
    # If pin is a string the IP is used
    elif isinstance(pin, str):
        turn_ip(pin, state)


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
