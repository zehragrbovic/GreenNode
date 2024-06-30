import time
import Adafruit_DHT
import RPi.GPIO as GPIO
import smbus
from mq import *
import spidev
from numpy import interp
import json
import requests
import asyncio
import aiohttp
from azure.iot.device import IoTHubDeviceClient, Message
import os

CONNECTION_STRING = "HostName=GreenNodeHub.azure-devices.net;DeviceId=rpi3;SharedAccessKey=UT8Fno/kz5nZX1NYTSjpdcGxiZhVKsIedAIoTKsjPbE="

POWER_PIN = 12  	# GPIO pin that provides power to the rain sensor
DO_PIN_RAIN = 7     # GPIO pin connected to the DO pin of the rain sensor
DO_PIN_GAS = 25  	# GPIO pin connected to the DO pin of the gas sensor
DO_PIN_SOIL = 21	# GPIO pin connected to the DO pin of the soil sensor

# Light sensor
DEVICE = 0x23  # Default device I2C address

POWER_DOWN = 0x00  # No active state
POWER_ON = 0x01  # Power on
RESET = 0x07  # Reset data register value

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

# bus = smbus.SMBus(0) # Rev 1 Pi uses 0
bus = smbus.SMBus(1)  # Rev 2 Pi uses 1

waiting = 300
ptemp = 101
phum = 101

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(POWER_PIN, GPIO.OUT)  # configure the power pin as an OUTPUT
    GPIO.setup(DO_PIN_RAIN, GPIO.IN)
    GPIO.setup(DO_PIN_GAS, GPIO.IN)
    GPIO.setup(DO_PIN_SOIL, GPIO.IN)
    waiting = 300

def convertToNumber(data):
    # Simple function to convert 2 bytes of data
    # into a decimal number. Optional parameter 'decimals'
    # will round to specified number of decimal places.
    result = (data[1] + (256 * data[0])) / 1.2
    return result

def readLight(addr=DEVICE):
    # Read data from I2C interface
    data = bus.read_i2c_block_data(addr, ONE_TIME_HIGH_RES_MODE_1)
    return convertToNumber(data)

# Read MCP3008 data
def analogInput(channel):
    spi = spidev.SpiDev()  # Created an object
    spi.open(0, 0)
    
    spi.max_speed_hz = 1350000
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data
    
async def async_post_request(url, headers, sensor_data):
	try:
		async with aiohttp.ClientSession() as session:
			async with session.post(url, headers = headers) as response:
				print(f"Data sent to IoT, executing post")
				await send_to_azure(sensor_data)
				await session.close()
				return await response.text();
	except Exception as ex:
		print(f"Exception in post: : {ex}")

async def send_to_azure(sensor_data):
    try:
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        json_data = json.dumps(sensor_data)
        message = Message(json_data)
        print(f"Sending message: {json_data}")
        client.send_message(message)
        print(f"Message successfully sent to IoT Hub")
        client.shutdown()
    except Exception as ex:
        print("Exception sending message:", ex)

def loop():
    # rain
    GPIO.output(POWER_PIN, GPIO.HIGH)  # turn the rain sensor's power ON
    time.sleep(0.01)  # wait 10 milliseconds

    rain_state = GPIO.input(DO_PIN_RAIN)

    GPIO.output(POWER_PIN, GPIO.LOW)  # turn the rain sensor's power OFF

    if rain_state == GPIO.HIGH:
        rainDet = 0
        print("Rain state: No Rain Detected")
    else:
        rainDet = 1
        print("Rain state: Rain Detected")

    # temperature and humidity
    hum, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 14)  # get data from DHT11
    print("Humidity:", hum)
    print("Temperature:", temp)

    # gas (air quality)
    gas_present = GPIO.input(DO_PIN_GAS)
    if gas_present == GPIO.LOW:
        gas_state = "Gas Present"
    else:
        gas_state = "No Gas Detected"

    print(f"Gas State: {gas_state}")

    mq = MQ()
    perc = mq.MQPercentage()
    lpg = perc["GAS_LPG"]
    co = perc["CO"]
    sm = perc["SMOKE"]
    print(f"LPG: {lpg} ppm, CO: {co} ppm, Smoke: {sm} ppm")

    # soil moisture
    if GPIO.input(DO_PIN_SOIL):
        print("Soil state: Dry")
    else:
        print("Soil state: Wet")

    output = analogInput(0)  # Reading from CH0
    output = interp(output, [0, 1023], [100, 0])
    output = int(output)
    print("Moisture:", output)

    # light intensity
    lightLevel = readLight()
    print("Light Level : " + format(lightLevel, '.2f') + " lx")

    print()

    sensor_data = {
        "temperature": temp,
        "humidity": hum,
        "carbon_monoxide": co,
        "methane": sm,
        "lpg": lpg,
        "rain_detected": rainDet,
        "soil_moisture": output,
        "illuminance": lightLevel,
        "location": "home",
        "additional_note": "optimized - test 2"
    }
    url = "https://env-monitoring-server-accba762091c.herokuapp.com/api/measurements"
    headers = {
        # # "Content-Type": "application/json",
         "ngrok-skip-browser-warning": "bilosta"
    }
    
    
    asyncio.run(async_post_request(url, headers, sensor_data))
    # send_to_azure(sensor_data)

    

    global ptemp
    global phum
    global waiting

    if ptemp == temp and phum == hum and waiting < 3600:
        waiting *= 2
    else:
        waiting = 300

    ptemp = temp
    phum = hum

    time.sleep(waiting)  # pause for 10 seconds to avoid reading sensors frequently and prolong the sensor lifetime

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        setup()
        while True:
            loop()
    except KeyboardInterrupt:
        cleanup()
