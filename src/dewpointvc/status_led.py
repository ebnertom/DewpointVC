import time

from digitalio import DigitalInOut, Direction

class StatusLed:
    def __init__(self, pin):
        self.io = DigitalInOut(pin)
        self.io.direction = Direction.OUTPUT

    def on(self):
        self.io.value = True

    def off(self):
        self.io.value = False

    def blink(self, n, interval, led_status_afterwards):
        for i in range(n):
            time.sleep(interval/2)
            self.io.value = False
            time.sleep(interval/2)
            self.io.value = True

        self.io.value = led_status_afterwards

