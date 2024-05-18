import time
import Adafruit_DHT

import RPi.GPIO as GPIO
import time


POWER_PIN = 12  	# GPIO pin that provides power to the rain sensor
DO_PIN_RAIN = 7     # GPIO pin connected to the DO pin of the rain sensor
DO_PIN_GAS = 25  	# GPIO pin connected to the DO pin of the gas sensor
DO_PIN_SOIL = 21	# GPIO pin connected to the DO pin of the soil sensor

def setup():

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(POWER_PIN, GPIO.OUT)  # configure the power pin as an OUTPUT
    GPIO.setup(DO_PIN_RAIN, GPIO.IN)
    GPIO.setup(DO_PIN_GAS, GPIO.IN)
    GPIO.setup(DO_PIN_SOIL, GPIO.IN)

def loop():
	
	# rain
    GPIO.output(POWER_PIN, GPIO.HIGH)  # turn the rain sensor's power ON
    time.sleep(0.01)                   # wait 10 milliseconds

    rain_state = GPIO.input(DO_PIN_RAIN)

    GPIO.output(POWER_PIN, GPIO.LOW)  # turn the rain sensor's power OFF

    if rain_state == GPIO.HIGH:
        print("The rain is NOT detected")
    else:
        print("The rain is detected")
        
    # temperature and humidity
    hum, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 14)  #get data from DHT11
    print("Humidity:", hum)
    print("Temperature:", temp)
    
    # gas (air quality)
    gas_present = GPIO.input(DO_PIN_GAS)
    if gas_present == GPIO.LOW:
        gas_state = "Gas Present"
    else:
        gas_state = "No Gas"

    print(f"Gas State: {gas_state}")
    
    # soil moisture
    if GPIO.input(DO_PIN_SOIL):
            print ("Soil is dry")
    else:
            print ("Soil is wet")

    time.sleep(3)  # pause for 1 second to avoid reading sensors frequently and prolong the sensor lifetime

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        cleanup()

