import matplotlib
import numpy as np
import matplotlib.pyplot as plt

matplotlib.use('QtAgg')


def calc_dew_point(temperature, relative_humidity):
    A = 17.27
    B = 237.7
    alpha = ((A * temperature) / (B + temperature)) + np.log(relative_humidity / 100.0)
    dew_point = (B * alpha) / (A - alpha)
    return dew_point



temp = np.linspace(-10, 30, 50)

humidities = (30, 40, 50, 60, 70, 80)
for humidity in humidities:
    dew_point = calc_dew_point(temp, humidity)

    plt.plot(temp, dew_point)
plt.legend(humidities)
plt.xlabel('temperature (C)')
plt.ylabel('dew-point (C)')

plt.figure()

humidity = np.linspace(10, 100, 50)
temp = 10
dew_point = calc_dew_point(temp, humidity)
plt.plot(humidity, dew_point)
plt.xlabel('humidity')
plt.ylabel('dew-point (C)')
plt.grid(True)
plt.show()
