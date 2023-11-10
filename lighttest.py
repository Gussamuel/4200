#lighttest

import RPi.GPIO as GPIO
import time

# Define the pins for LED and PIR sensor
LED = 23
PIR = 24

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(PIR, GPIO.IN)

try:
    while True:
        if GPIO.input(PIR):
            GPIO.output(LED, GPIO.HIGH)
        else:
            GPIO.output(LED, GPIO.LOW)
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
