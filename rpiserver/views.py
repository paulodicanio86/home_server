import os
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO
from flask import Flask, render_template, request, redirect, url_for


from rpiserver import app, load_data, path_json, path
from rpiserver import initiate_pin_states, read_pin_states, write_data, GPIO_on, GPIO_off

@app.route("/")
def main():
    GPIO.setmode(GPIO.BOARD)
    initiate_pin_states(path_json)

    pins_in = load_data(path_json)
    pins_in = read_pin_states(pins_in)

    template_data = {
        'pins': pins_in
        }
    return render_template(os.path.join(path, 'templates', 'main.html'), **template_data)


@app.route("/<change_pin>/<action>")
def change_pin_domain(change_pin, action):
    change_pin = int(change_pin)
    pins_in = load_data(path_json)

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
                data_in = load_data(path_json)
                data_in[key]['last_on'] = now_str
                write_data(path_json, data_in)

    return redirect(url_for('main'))


@app.route("/edit/<entry>", methods=['GET'])
def edit_domain_get(entry):

    pins_in = load_data(path_json)

    template_data = {
        'entry': pins_in[entry],
        'entry_name': entry
        }

    if pins_in[entry]['mode'] == 'on_off':
        return render_template(os.path.join(path, 'templates', 'edit_on_off.html'), **template_data)
    elif pins_in[entry]['mode'] == 'duration':
        return render_template(os.path.join(path, 'templates', 'edit_duration.html'), **template_data)


@app.route("/edit", methods=['POST'])
def edit_domain_post():

    entry_name = request.form['entry_name']
    data_in = load_data(path_json)

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

    write_data(path_json, data_in)
    return redirect(url_for('edit_domain_get', entry=entry_name))




