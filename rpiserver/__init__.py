import json
import os
import subprocess
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


def initiate_gpio_board():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)


### DELETE? NOT BEING USED AFTERALL
def ip_available(ip):
    response = subprocess.run(["/bin/ping -c 1 -t 1 " + ip], shell=True).returncode
    if response == 0:
        return True
    else:
        return False


def read_gpio_state(pin):
    GPIO.setup(pin, GPIO.OUT)
    state = GPIO.input(pin)

    if state == GPIO_on:
        return True
    if state == GPIO_off:
        return False


def read_ip_state(ip):
    state = 'OFF'
    try:
        r = requests.get("http://" + ip, timeout=0.1)
        r_str = str(r.text)
        state = r_str.split('<br>')[0].split('now: ')[1]
    except:
        state = 'OFF'

    if state == 'ON':
        return True
    if state == 'OFF':
        return False


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
    try:
        requests.get("http://" + ip + "/RELAY=" + state, timeout=0.1)
    except:
        pass


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
