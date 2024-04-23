import time
import pytest
from unittest.mock import MagicMock
from dewpointvc.ventilation_control_logic import VentilationControlLogic, FanState


def test_control_fan_turn_on():
    # Create an instance of VentilationControlLogic with mock data
    vcl = VentilationControlLogic(
        dewpoint_threshold=2,
        min_on_duration=10,
        max_on_duration=60,
        min_off_duration=20
    )

    # Set up mock TempHumidityMeasurement objects for inside and outside climates
    outside_climate = MagicMock()
    outside_climate.dewpoint = 5
    outside_climate.temperature = 20
    inside_climate = MagicMock()
    inside_climate.dewpoint = 10
    inside_climate.temperature = 18

    # Call control_fan method with dew point differential above threshold
    vcl.control_fan(outside_climate, inside_climate)

    # Assert that the fan state is ON
    assert vcl.fan_state == FanState.ON


def test_control_fan_turn_off():
    # Create an instance of VentilationControlLogic with mock data
    vcl = VentilationControlLogic(
        dewpoint_threshold=2,
        min_on_duration=10,
        max_on_duration=60,
        min_off_duration=20
    )

    # Set up mock TempHumidityMeasurement objects for inside and outside climates
    outside_climate = MagicMock()
    outside_climate.dewpoint = 5
    outside_climate.temperature = 20
    inside_climate = MagicMock()
    inside_climate.dewpoint = 10
    inside_climate.temperature = 18

    # Call control_fan method with dew point differential below threshold
    vcl.control_fan(outside_climate, inside_climate)

    # Assert that the fan state is OFF
    assert vcl.fan_state == FanState.OFF


def test_control_fan_min_on_duration():
    # Create an instance of VentilationControlLogic with mock data
    vcl = VentilationControlLogic(
        dewpoint_threshold=2,
        min_on_duration=5,
        max_on_duration=60,
        min_off_duration=20
    )

    # Set up mock TempHumidityMeasurement objects for inside and outside climates
    outside_climate = MagicMock()
    outside_climate.dewpoint = 5
    outside_climate.temperature = 20
    inside_climate = MagicMock()
    inside_climate.dewpoint = 10
    inside_climate.temperature = 18

    # Call control_fan method with dew point differential above threshold
    vcl.control_fan(outside_climate, inside_climate)
    assert vcl.fan_state == FanState.ON  # Fan should be turned ON

    # Simulate time passing by waiting for less than the min_on_duration
    time.sleep(3)

    # Call control_fan method again with the same dew point differential
    vcl.control_fan(outside_climate, inside_climate)
    assert vcl.fan_state == FanState.ON  # Fan should still be ON since min_on_duration not reached

    # Simulate time passing by waiting for the remaining time until min_on_duration
    time.sleep(2)

    # Call control_fan method again with the same dew point differential
    vcl.control_fan(outside_climate, inside_climate)
    assert vcl.fan_state == FanState.ON  # Fan should still be ON since min_on_duration reached


def test_control_fan_max_on_duration():
    # Create an instance of VentilationControlLogic with mock data
    vcl = VentilationControlLogic(
        dewpoint_threshold=2,
        min_on_duration=3,
        max_on_duration=5,
        min_off_duration=20
    )

    # Set up mock TempHumidityMeasurement objects for inside and outside climates
    outside_climate = MagicMock()
    outside_climate.dewpoint = 5
    outside_climate.temperature = 20
    inside_climate = MagicMock()
    inside_climate.dewpoint = 10
    inside_climate.temperature = 18

    # Call control_fan method with dew point differential above threshold
    vcl.control_fan(outside_climate, inside_climate)
    assert vcl.fan_state == FanState.ON  # Fan should be turned ON

    # Simulate time passing by waiting for more than the max_on_duration
    time.sleep(5.1)

    # Call control_fan method again with the same dew point differential
    vcl.control_fan(outside_climate, inside_climate)
    assert vcl.fan_state == FanState.OFF  # Fan should be turned OFF since max_on_duration reached
