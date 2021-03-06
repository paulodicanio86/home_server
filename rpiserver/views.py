from time import sleep
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for


from rpiserver import app, load_data, path_json
from rpiserver import initiate_gpio_board, read_pin_states, write_data, turn_device


@app.route("/")
def main():
    initiate_gpio_board()

    pins_in = load_data(path_json)
    pins_in = read_pin_states(pins_in)

    template_data = {
        'pins': pins_in
        }
    return render_template('main.html', **template_data)


@app.route("/<name_key>/<action>")
def change_pin_domain(name_key, action):
    initiate_gpio_board()

    pins_in = load_data(path_json)
    device_name = pins_in[name_key]['pin']

    if action == "on":
        turn_device(device_name, 'ON')

    if action == "off":
        turn_device(device_name, 'OFF')

    if action == "duration":
        sleep_duration = pins_in[name_key]['duration']
        turn_device(device_name, 'ON')
        sleep(sleep_duration)
        turn_device(device_name, 'OFF')

        # Capture last_on time
        now_str = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        data_in = load_data(path_json)
        data_in[name_key]['last_on'] = now_str
        write_data(path_json, data_in)

    return redirect(url_for('main'))


@app.route("/edit/<name_key>", methods=['GET'])
def edit_domain_get(name_key):
    pins_in = load_data(path_json)

    template_data = {
        'entry': pins_in[name_key],
        'entry_name': name_key
        }

    if pins_in[name_key]['mode'] == 'on_off':
        return render_template('edit_on_off.html', **template_data)
    elif pins_in[name_key]['mode'] == 'duration':
        return render_template('edit_duration.html', **template_data)


@app.route("/edit", methods=['POST'])
def edit_domain_post():
    data_in = load_data(path_json)
    name_key = request.form['entry_name']

    if data_in[name_key]['mode'] == 'duration':
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
        data_in[name_key]['on'] = on_times
        data_in[name_key]['duration'] = int(duration)

    if data_in[name_key]['mode'] == 'on_off':
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
        data_in[name_key]['on'] = on_times

        off_times = []
        if off_time_1 != '':
            off_times.append(off_time_1)
        if off_time_2 != '':
            off_times.append(off_time_2)
        if off_time_3 != '':
            off_times.append(off_time_3)
        data_in[name_key]['off'] = off_times

    write_data(path_json, data_in)
    return redirect(url_for('edit_domain_get', name_key=name_key))




