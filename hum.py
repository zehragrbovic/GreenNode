import time
import Adafruit_DHT

while True:
    hum, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 14)
    print(hum, temp)
    time.sleep(1)
