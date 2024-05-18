import time
import Adafruit_DHT
import RPi.GPIO as GPIO
import smbus


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

def loop():
	
	# rain
    GPIO.output(POWER_PIN, GPIO.HIGH)  # turn the rain sensor's power ON
    time.sleep(0.01)                   # wait 10 milliseconds

    rain_state = GPIO.input(DO_PIN_RAIN)

    GPIO.output(POWER_PIN, GPIO.LOW)  # turn the rain sensor's power OFF

    if rain_state == GPIO.HIGH:
        print("Rain state: No Rain Detected")
    else:
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
    
    # soil moisture
    if GPIO.input(DO_PIN_SOIL):
            print ("Soil state: Dry")
    else:
            print ("Soil state: Wet")
            
    # light intensity
    lightLevel=readLight()
    print("Light Level : " + format(lightLevel,'.2f') + " lx")
    
    
    print()
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

