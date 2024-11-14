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
                 params):
        """

        Parameters
        ----------
        params : ParameterCollection
            all parameters
        """
        self.log = logging.getLogger(__name__)
        self.params = params

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
        dewpoint_on_threshold = self.params.get_param('dewpoint_on_threshold')
        dewpoint_off_threshold = self.params.get_param('dewpoint_off_threshold')
        min_on_duration = self.params.get_param('min_on_duration')
        max_on_duration = self.params.get_param('max_on_duration')
        min_off_duration = self.params.get_param('min_off_duration')
        min_inside_temperature = self.params.get_param('min_inside_temperature')
        min_outside_temperature = self.params.get_param('min_outside_temperature')

        if self.last_ventilation_change_time is not None:
            dur_since_change = time.time() - self.last_ventilation_change_time
            if self.fan_state == FanState.OFF and dur_since_change < min_off_duration:
                self.log.debug('min min_off_duration not reached yet, don\'t change ventilation state yet')
                return
            if self.fan_state == FanState.ON and dur_since_change < min_on_duration:
                self.log.debug('min min_on_duration not reached yet, don\'t change ventilation state yet')
                return
            if self.fan_state == FanState.ON and dur_since_change >= max_on_duration:
                self.log.info(f'Turning OFF fan - max_on_duration ({max_on_duration:0.1f}s) reached')
                self.fan_state = FanState.OFF
                self.last_ventilation_change_time = time.time()
                return

        dew_point_differential = inside_climate.dewpoint - outside_climate.dewpoint
        self.log.debug(f'dew-point differential: {dew_point_differential:0.1f}°C')

        if self.fan_state == FanState.OFF and dew_point_differential > dewpoint_on_threshold:
            if inside_climate.temperature >= min_inside_temperature and outside_climate.temperature >= min_outside_temperature:
                self.log.info(f'dewpoint differential {dew_point_differential:0.1f}°C above threshold {dewpoint_on_threshold:0.1f}°C --> turning ON fan')
                self.fan_state = FanState.ON
                self.last_ventilation_change_time = time.time()
                return
            else:
                self.log.info(f'dewpoint differential {dew_point_differential:0.1f}°C above threshold {dewpoint_on_threshold:0.1f}°C, however it\'s already too cold inside')

        if self.fan_state == FanState.ON and dew_point_differential <= dewpoint_off_threshold:
            self.log.info(f'dewpoint differential {dew_point_differential:0.1f}°C below threshold {dewpoint_off_threshold:0.1f}°C --> turning OFF fan')
            self.fan_state = FanState.OFF
            self.last_ventilation_change_time = time.time()
            return
