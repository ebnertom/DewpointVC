import math


class TempHumidityMeasurement:
    def __init__(self, location_name, temperature, relative_humidity):
        """

        Parameters
        ----------
        location_name : str
            name of the location, where temp and humidity was read
        temperature : float
            temperature in degree Celsius
        relative_humidity : float
            relative humidity in percent
        """
        self.location_name = location_name
        self.temperature = temperature
        self.relative_humidity = relative_humidity

    @property
    def dewpoint(self):
        # code taken from https://gist.github.com/sourceperl/45587ea99ff123745428
        A = 17.27
        B = 237.7
        alpha = ((A * self.temperature) / (B + self.temperature)) + math.log(self.relative_humidity / 100.0)
        return (B * alpha) / (A - alpha)

