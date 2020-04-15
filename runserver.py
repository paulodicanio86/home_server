# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)


from rpiserver import app

app.run(host="0.0.0.0", threaded=True)


# GPIO housekeeping
GPIO.cleanup()