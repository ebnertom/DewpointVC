import math
import time

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS



if __name__ == '__main__':
    org = "toris"
    bucket = "dewpointvc"
    client = influxdb_client.InfluxDBClient(
        url="http://localhost:8086",
        token="6LGefO8r6ECc44VofaIW7zCcNdxcUaofzJYDeVd9WCobOJQrQSwG3AiGlhD1WrN_jCSKcwKzHRxZ2AkLiMf86w==",
        org=org
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)

    i = 0
    while True:
        p = influxdb_client.Point("my_measurement").tag("location", "outside").field("temperature", math.sin(i / 180 * math.pi)).field("abc", 42)
        write_api.write(bucket=bucket, org=org, record=p)
        time.sleep(1)
        i += 1
