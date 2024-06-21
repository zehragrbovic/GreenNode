import time
import Adafruit_DHT
import RPi.GPIO as GPIO
import smbus
from mq import *
import spidev 
from numpy import interp  
import json
import requests


POWER_PIN = 12  	# GPIO pin that provides power to the rain sensor
DO_PIN_RAIN = 7     # GPIO pin connected to the DO pin of the rain sensor
DO_PIN_GAS = 25  	# GPIO pin connected to the DO pin of the gas sensor
DO_PIN_SOIL = 21	# GPIO pin connected to the DO pin of the soil sensor

# Light sensor
DEVICE     = 0x23 # Default device I2C address

POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value

# Start measurement at 4lx resolution. Time typically 16ms.
CONTINUOUS_LOW_RES_MODE = 0x13
# Start measurement at 1lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_1 = 0x10
# Start measurement at 0.5lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_2 = 0x11
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_1 = 0x20
# Start measurement at 0.5lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_2 = 0x21
# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_LOW_RES_MODE = 0x23

#bus = smbus.SMBus(0) # Rev 1 Pi uses 0
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1

def setup():

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(POWER_PIN, GPIO.OUT)  # configure the power pin as an OUTPUT
    GPIO.setup(DO_PIN_RAIN, GPIO.IN)
    GPIO.setup(DO_PIN_GAS, GPIO.IN)
    GPIO.setup(DO_PIN_SOIL, GPIO.IN)
    
def convertToNumber(data):
  # Simple function to convert 2 bytes of data
  # into a decimal number. Optional parameter 'decimals'
  # will round to specified number of decimal places.
  result=(data[1] + (256 * data[0])) / 1.2
  return (result)

def readLight(addr=DEVICE):
  # Read data from I2C interface
  data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE_1)
  return convertToNumber(data)

# Read MCP3008 data
def analogInput(channel):
  spi = spidev.SpiDev() # Created an object
  spi.open(0,0)
	
  spi.max_speed_hz = 1350000
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

def loop():
	
	# rain
    GPIO.output(POWER_PIN, GPIO.HIGH)  # turn the rain sensor's power ON
    time.sleep(0.01)                   # wait 10 milliseconds

    rain_state = GPIO.input(DO_PIN_RAIN)

    GPIO.output(POWER_PIN, GPIO.LOW)  # turn the rain sensor's power OFF

    if rain_state == GPIO.HIGH:
		#rd = false
        print("Rain state: No Rain Detected")
    else:
		#rd = true
        print("Rain state: Rain Detected")
        
    # temperature and humidity
    hum, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 14)  #get data from DHT11
    print("Humidity:", hum)
    print("Temperature:", temp)
    
    # gas (air quality)
    gas_present = GPIO.input(DO_PIN_GAS)
    if gas_present == GPIO.LOW:
        gas_state = "Gas Present"
    else:
        gas_state = "No Gas Detected"

    print(f"Gas State: {gas_state}")
    
    mq = MQ();
    perc = mq.MQPercentage()
    lpg = perc["GAS_LPG"]
    co = perc["CO"]
    sm = perc["SMOKE"]
    print(f"LPG: {lpg} ppm, CO: {co} ppm, Smoke: {sm} ppm")
    
    # soil moisture
    if GPIO.input(DO_PIN_SOIL):
            print ("Soil state: Dry")
    else:
            print ("Soil state: Wet")
            

    output = analogInput(0) # Reading from CH0
    output = interp(output, [0, 1023], [100, 0])
    output = int(output)
    print("Moisture:", output)
            
    # light intensity
    #lightLevel=readLight()
    #print("Light Level : " + format(lightLevel,'.2f') + " lx")
    
    
    print()
    
    sensor_data = {
		"temperature": temp,
		"humidity": hum,
		"carbon_monoxide": co,
		"methane": sm,
		"lpg": lpg,
		"rain_detected": 0,
		"soil_moisture": 0,
		"illuminance": 200.0
    }
    
    json_data = json.dumps(sensor_data)
    
    url = "https://9917-77-239-19-198.ngrok-free.app/api/measurements"
    headers = {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "bilosta"
    }
    
    #response = requests.post(url, data = json_data, headers = headers)
    
    #if response.status_code == 200:
    #    print("Data sent successfully")
    #else:
    #    print("Response", response.text)
    
    time.sleep(10)  # pause for 10 seconds to avoid reading sensors frequently and prolong the sensor lifetime

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        cleanup()

