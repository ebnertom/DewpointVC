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

        self.max_dewpoint_temp_gradient_per_s = 0.5  # max absolute temperature gradient of dewpoint in °C / s
        self.min_duration_between_readouts = 2.5  # in seconds

        self.last_measurement = None
        self.last_measurement_time = None

    def read(self):
        """
        read temperature using a retry strategy in case of errors

        Returns
        -------
        TempHumidityMeasurement
            the temperature and humidity
        """
        if self.last_measurement_time and (time.time() - self.last_measurement_time) < self.min_duration_between_readouts:
            time.sleep(self.min_duration_between_readouts - (time.time() - self.last_measurement_time))

        got_valid_measurement = False
        while not got_valid_measurement:
            measurement = self._read()
            if self.last_measurement is not None:
                now = time.time()
                dewpoint_temp_grad = (measurement.dewpoint - self.last_measurement.dewpoint) / (now - self.last_measurement_time)

                if abs(dewpoint_temp_grad) <= self.max_dewpoint_temp_gradient_per_s:
                    got_valid_measurement = True
                else:
                    self.log.error(f'{self.log_prefix} dewpoint gradient exceeded maximum, temp_gradient: {dewpoint_temp_grad:0.2f} °/s')
                    time.sleep(self.min_duration_between_readouts)
                    continue
            else:
                got_valid_measurement = True

            self.last_measurement_time = time.time()
            self.last_measurement = measurement

        return measurement

    def _read(self):
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

