from time import sleep
from datetime import datetime
import json
import RPi.GPIO as GPIO
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)


# GPIO housekeeping
GPIO.setmode(GPIO.BOARD)
# Reverse logic here for relay because of 3.3V difference
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


def initiate_pin_states(file_path):
    pins_in = load_data(file_path)
    for key in pins_in:
        pins_in[key]['state'] = GPIO_off
        GPIO.setup(pins_in[key]['pin'], GPIO.OUT)
        GPIO.output(pins_in[key]['pin'], GPIO_off)


def read_pin_states(pins_in):
    for key in pins_in:
        pins_in[key]['state'] = GPIO.input(pins_in[key]['pin'])
    return pins_in


# Initiate variables for server start
path = '/home/pi/home_server/schedule.json'
initiate_pin_states(path)


@app.route("/")
def main():
    pins_in = load_data(path)
    pins_in = read_pin_states(pins_in)

    template_data = {
        'pins': pins_in
        }
    return render_template('main.html', **template_data)


@app.route("/<change_pin>/<action>")
def change_pin_domain(change_pin, action):
    change_pin = int(change_pin)
    pins_in = load_data(path)

    if action == "on":
        GPIO.output(change_pin, GPIO_on)

    if action == "off":
        GPIO.output(change_pin, GPIO_off)

    if action == "duration":
        sleep_duration = 0
        for key in pins_in:
            if pins_in[key]['pin'] == change_pin and 'duration' in pins_in[key].keys():
                sleep_duration = pins_in[key]['duration']
        GPIO.output(change_pin, GPIO_on)
        sleep(sleep_duration)
        GPIO.output(change_pin, GPIO_off)

        # capture last_on time
        now = datetime.now()
        now_str = now.strftime("%d/%m/%Y, %H:%M:%S")
        for key in pins_in:
            if pins_in[key]['pin'] == change_pin and 'last_on' in pins_in[key].keys():
                data_in = load_data(path)
                data_in[key]['last_on'] = now_str
                write_data(path, data_in)

    return redirect(url_for('main'))


@app.route("/edit/<entry>", methods=['GET'])
def edit_domain_get(entry):

    pins_in = load_data(path)

    template_data = {
        'entry': pins_in[entry],
        'entry_name': entry
        }

    if pins_in[entry]['mode'] == 'on_off':
        return render_template('edit_on_off.html', **template_data)
    elif pins_in[entry]['mode'] == 'duration':
        return render_template('edit_duration.html', **template_data)


@app.route("/edit", methods=['POST'])
def edit_domain_post():

    entry_name = request.form['entry_name']
    data_in = load_data(path)

    if data_in[entry_name]['mode'] == 'duration':
        on_time_1 = request.form['on_time_1']
        on_time_2 = request.form['on_time_2']
        on_time_3 = request.form['on_time_3']
        duration = request.form['duration']

        on_times = []
        if on_time_1 != '':
            on_times.append(on_time_1)
        if on_time_2 != '':
            on_times.append(on_time_2)
        if on_time_3 != '':
            on_times.append(on_time_3)
        data_in[entry_name]['on'] = on_times
        data_in[entry_name]['duration'] = int(duration)

    if data_in[entry_name]['mode'] == 'on_off':
        on_time_1 = request.form['on_time_1']
        on_time_2 = request.form['on_time_2']
        on_time_3 = request.form['on_time_3']
        off_time_1 = request.form['off_time_1']
        off_time_2 = request.form['off_time_2']
        off_time_3 = request.form['off_time_3']

        on_times = []
        if on_time_1 != '':
            on_times.append(on_time_1)
        if on_time_2 != '':
            on_times.append(on_time_2)
        if on_time_3 != '':
            on_times.append(on_time_3)
        data_in[entry_name]['on'] = on_times

        off_times = []
        if off_time_1 != '':
            off_times.append(off_time_1)
        if off_time_2 != '':
            off_times.append(off_time_2)
        if off_time_3 != '':
            off_times.append(off_time_3)
        data_in[entry_name]['off'] = off_times

    write_data(path, data_in)
    return redirect(url_for('edit_domain_get', entry=entry_name))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

# GPIO housekeeping
GPIO.cleanup()
