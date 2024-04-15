import sys
import time

import adafruit_dht
import board


if __name__ == "__main__":
    dht_device = adafruit_dht.DHT22(board.D7)

    while True:
        try:
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity

            print(f'temperature: {temperature_c:0.1f}, humidity: {humidity:0.1f}')
        except:
            print(f'Exception occurred: {sys.exc_info()[0]}')
        time.sleep(2)
