import enum
import logging
import time

from dewpointvc.fan_state import FanState
from dewpointvc.temp_humidity_measurement import TempHumidityMeasurement


class VentilationControlLogic:
    """
    Class to control cellar ventilation system based on dew point differentials.
    """

    def __init__(self,
                 dewpoint_on_threshold=2.0,
                 dewpoint_off_threshold=1.5,
                 min_on_duration=60,
                 max_on_duration=60*60,
                 min_off_duration=120,
                 min_inside_temperature=6):
        """

        Parameters
        ----------
        dewpoint_on_threshold : float
            Dew point differential threshold.
            i.e. how much the dewpoint must be larger inside then outside such that ventilation is turned on
        dewpoint_off_threshold : float
            Dew point differential threshold.
            i.e. how much the dewpoint must be larger inside then outside such that ventilation is turned off
        min_on_duration : float
            Minimum duration for the fan to remain on once activated, in seconds.
        max_on_duration float
            Maximum duration for continuous operation of the fan, in seconds.
        min_inside_temperature : float
            minimum temperature inside the cellar
        """
        self.log = logging.getLogger(__name__)
        self.dewpoint_on_threshold = dewpoint_on_threshold
        self.dewpoint_off_threshold = dewpoint_off_threshold
        self.min_on_duration = min_on_duration
        self.max_on_duration = max_on_duration
        self.min_off_duration = min_off_duration
        self.min_inside_temperature = min_inside_temperature

        self.fan_state = FanState.OFF
        self.last_ventilation_change_time = None

    def control_fan(self, outside_climate, inside_climate):
        """
        Control the fan based on dew point differentials.

        Parameters
        ----------
        outside_climate : TempHumidityMeasurement
            temperature / humidity outside
        inside_climate : TempHumidityMeasurement
            temperature / humidity inside the cellar.
        """
        if self.last_ventilation_change_time is not None:
            dur_since_change = time.time() - self.last_ventilation_change_time
            if self.fan_state == FanState.OFF and dur_since_change < self.min_off_duration:
                self.log.debug('min min_off_duration not reached yet, don\'t change ventilation state yet')
                return
            if self.fan_state == FanState.ON and dur_since_change < self.min_on_duration:
                self.log.debug('min min_on_duration not reached yet, don\'t change ventilation state yet')
                return
            if self.fan_state == FanState.ON and dur_since_change >= self.max_on_duration:
                self.log.info(f'Turning OFF fan - max_on_duration ({self.max_on_duration:0.1f}s) reached')
                self.fan_state = FanState.OFF
                self.last_ventilation_change_time = time.time()
                return

        dew_point_differential = inside_climate.dewpoint - outside_climate.dewpoint
        self.log.debug(f'dew-point differential: {dew_point_differential:0.1f}°C')

        if self.fan_state == FanState.OFF and dew_point_differential > self.dewpoint_on_threshold:
            if inside_climate.temperature >= self.min_inside_temperature:
                self.log.info(f'dewpoint differential {dew_point_differential:0.1f}°C above threshold {self.dewpoint_on_threshold:0.1f}°C --> turning ON fan')
                self.fan_state = FanState.ON
                self.last_ventilation_change_time = time.time()
                return
            else:
                self.log.info(f'dewpoint differential {dew_point_differential:0.1f}°C above threshold {self.dewpoint_on_threshold:0.1f}°C, however it\'s already too cold inside')

        if self.fan_state == FanState.ON and dew_point_differential <= self.dewpoint_off_threshold:
            self.log.info(f'dewpoint differential {dew_point_differential:0.1f}°C below threshold {self.dewpoint_off_threshold:0.1f}°C --> turning OFF fan')
            self.fan_state = FanState.OFF
            self.last_ventilation_change_time = time.time()
            return
