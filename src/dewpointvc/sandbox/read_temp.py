import sys
import time
import traceback

import adafruit_dht
import board


if __name__ == "__main__":
    dht_device = adafruit_dht.DHT22(board.D16)

    while True:
        try:
            temperature_c = dht_device.temperature
            humidity = dht_device.humidity

            print(f'temperature: {temperature_c:0.1f}, humidity: {humidity:0.1f}')
        except:
            print(f'Exception occurred: {sys.exc_info()[0]}')
            traceback.print_exc()
        time.sleep(2)
