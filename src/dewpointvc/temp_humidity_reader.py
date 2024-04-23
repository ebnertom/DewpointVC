import time

import adafruit_dht
import logging

from dewpointvc.temp_humidity_measurement import TempHumidityMeasurement


class TemperatureReaderException(Exception):
    pass

class TempHumidityReader:
    def __init__(self, pin, location_name):
        self.pin = pin
        self.location_name = location_name
        self.log_prefix = f'[{self.location_name}]'
        self.dht_device = adafruit_dht.DHT22(pin)
        self.log = logging.getLogger(__name__)

    def read(self):
        """
        read temperature using a error retry strategy

        Returns
        -------
        TempHumidityMeasurement
            the temperature and humidity
        """
        max_retry_counter = 20

        while max_retry_counter > 0:
            try:
                temperature_c = self.dht_device.temperature
                humidity = self.dht_device.humidity
                if temperature_c is None or humidity is None:
                    raise RuntimeError(f'failed to read temperature or humidity from DHT22 on pin {self.pin}')
                self.log.info(f'{self.log_prefix} temperature: {temperature_c:0.1f}, humidity: {humidity:0.1f}')
                return TempHumidityMeasurement(self.location_name, temperature_c, humidity)
            except:
                self.log.debug(f'{self.log_prefix} failed to read temperature, retry-counter: {max_retry_counter}', exc_info=True)
                max_retry_counter -= 1
                time.sleep(0.5)

        raise TemperatureReaderException(f'failed to read temperature/humidity from DHT22 on pin {self.pin}')

