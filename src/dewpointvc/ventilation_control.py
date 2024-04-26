
from digitalio import DigitalInOut, Direction

from dewpointvc.fan_state import FanState


class VentilationControl:
    def __init__(self, pin, low_level_trigger=False):
        self.low_level_trigger = low_level_trigger
        self.io = DigitalInOut(pin)
        self.io.direction = Direction.OUTPUT

    def set(self, state):
        """

        Parameters
        ----------
        state : FanState
            state on or off

        Returns
        -------
        None
        """
        value = state == FanState.ON
        if self.low_level_trigger:
            value = not value

        self.io.value = value

