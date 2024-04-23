import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

from dewpointvc.temp_humidity_measurement import TempHumidityMeasurement


class InfluxDBMetricLogger:
    def __init__(self,
                 org,
                 bucket,
                 host,
                 port,
                 token):
        self.org = org
        self.bucket = bucket
        self._client = influxdb_client.InfluxDBClient(
        url=f"http://{host}:{port}",
        token=token,
        org=org
        )
        self._write_api = self._client.write_api(write_options=SYNCHRONOUS)

    def log_temperature_measurement(self, temperature):
        """

        Parameters
        ----------
        temperature : TempHumidityMeasurement

        Returns
        -------

        """
        p = influxdb_client.Point("temp_humidity").tag("location", temperature.location_name)
        p = p.field("temperature", temperature.temperature)
        p = p.field("relative_humidity", temperature.relative_humidity)
        p = p.field("dewpoint", temperature.dewpoint)

        self._write_api.write(bucket=self.bucket, org=self.org, record=p)

    def log_fan_state(self, fan_state):
        p = influxdb_client.Point("fan_status")
        p = p.field("fan_state", fan_state)

        self._write_api.write(bucket=self.bucket, org=self.org, record=p)
