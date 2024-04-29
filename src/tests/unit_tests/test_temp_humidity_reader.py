import time
from unittest.mock import Mock

from dewpointvc.temp_humidity_measurement import TempHumidityMeasurement
from dewpointvc.temp_humidity_reader import TempHumidityReader


def test_read_gradient_exceeded():
    r = TempHumidityReader('a', 'cellar')
    r._read = Mock()
    sleep_time = 2
    r._read.side_effect = [TempHumidityMeasurement('cellar', 10, 60.0),
                           TempHumidityMeasurement('cellar', 20, 60.1),
                           TempHumidityMeasurement('cellar', 10, 60.2),
                           TempHumidityMeasurement('cellar', 10, 60.3),
                           ]

    m = r.read()
    assert m.temperature == 10
    assert m.relative_humidity == 60.0
    assert r._read.call_count == 1

    time.sleep(sleep_time)
    m = r.read()
    assert r._read.call_count == 3
    assert m.temperature == 10
    assert m.relative_humidity == 60.2


def test_read_temperature_not_exceeded():
    r = TempHumidityReader('a', 'cellar')
    r._read = Mock()
    r._read.side_effect = [TempHumidityMeasurement('cellar', 10, 60.0),
                           TempHumidityMeasurement('cellar', 10, 60.1),
                           TempHumidityMeasurement('cellar', 10, 60.2),
                           TempHumidityMeasurement('cellar', 10, 60.3),
                           ]

    m = r.read()
    assert r._read.call_count == 1
    assert m.temperature == 10
    assert m.relative_humidity == 60.0

    m = r.read()
    assert r._read.call_count == 2
    assert m.temperature == 10
    assert m.relative_humidity == 60.1
