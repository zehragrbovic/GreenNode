# This Raspberry Pi code was developed by newbiely.com
# This Raspberry Pi code is made available for public use without any restriction
# For comprehensive instructions and wiring diagrams, please visit:
# https://newbiely.com/tutorials/raspberry-pi/raspberry-pi-rain-sensor


import RPi.GPIO as GPIO
import time

POWER_PIN = 12  # GPIO pin that provides power to the rain sensor
DO_PIN = 7     # GPIO pin connected to the DO pin of the rain sensor

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(POWER_PIN, GPIO.OUT)  # configure the power pin as an OUTPUT
    GPIO.setup(DO_PIN, GPIO.IN)

def loop():
    GPIO.output(POWER_PIN, GPIO.HIGH)  # turn the rain sensor's power ON
    time.sleep(0.01)                   # wait 10 milliseconds

    rain_state = GPIO.input(DO_PIN)

    GPIO.output(POWER_PIN, GPIO.LOW)  # turn the rain sensor's power OFF

    if rain_state == GPIO.HIGH:
        print("The rain is NOT detected")
    else:
        print("The rain is detected")

    time.sleep(1)  # pause for 1 second to avoid reading sensors frequently and prolong the sensor lifetime

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        cleanup()
