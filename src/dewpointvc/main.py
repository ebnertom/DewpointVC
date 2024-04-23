import logging
import os
import time
import board
from digitalio import DigitalInOut, Direction

from dewpointvc.fan_state import FanState
from dewpointvc.influxdb_metriclogger import InfluxDBMetricLogger
from dewpointvc.status_led import StatusLed
from dewpointvc.temp_humidity_reader import TempHumidityReader, TemperatureReaderException
from dewpointvc.ventilation_control import VentilationControl
from dewpointvc.ventilation_control_logic import VentilationControlLogic

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger(__name__)

    influx_logger = InfluxDBMetricLogger(
        os.environ.get('DEWPOINTVC_INFLUXDB_ORG'),
        os.environ.get('DEWPOINTVC_INFLUXDB_BUCKET'),
        os.environ.get('DEWPOINTVC_INFLUXDB_HOST'),
        os.environ.get('DEWPOINTVC_INFLUXDB_PORT'),
        os.environ.get('DEWPOINTVC_INFLUXDB_TOKEN'),
    )

    temp_cellar_reader = TempHumidityReader(board.D17, 'cellar')
    temp_outside_reader = TempHumidityReader(board.D10, 'outside')
    ventilation_control = VentilationControl(board.D14)
    ventilation_control.set(FanState.OFF)

    error_led = StatusLed(board.D15)
    error_led.off()


    ventilation_control_logic = VentilationControlLogic()

    while True:
        try:
            temp_cellar = temp_cellar_reader.read()
            temp_outside = temp_outside_reader.read()

            influx_logger.log_temperature_measurement(temp_cellar)
            influx_logger.log_temperature_measurement(temp_outside)

            ventilation_control_logic.control_fan(temp_outside, temp_cellar)
            log.info(f'fan state: {ventilation_control_logic.fan_state}')
            influx_logger.log_fan_state(int(ventilation_control_logic.fan_state.value))
            ventilation_control.set(ventilation_control_logic.fan_state)

            error_led.off()
            time.sleep(1)
        except TemperatureReaderException:
            error_led.on()
            log.warning('no temperature available, turning off fan and re-trying after 10s', exc_info=True)
            try:
                ventilation_control.set(FanState.OFF)
            except:
                log.error('failed to turn of fan', exc_info=True)
            error_led.blink(10, 1, True)
        except KeyboardInterrupt:
            log.info('received keyboard interrrupt, shutting down and turning off fan')
            try:
                ventilation_control.set(FanState.OFF)
            except:
                log.error('failed to turn of fan', exc_info=True)
            exit(0)
        except:
            error_led.value = True
            log.warning('unhandled exception, trying to turn off fan', exc_info=True)
            try:
                ventilation_control.set(FanState.OFF)
            except:
                log.error('failed to turn of fan', exc_info=True)
            error_led.blink(4*10, 0.25, True)
