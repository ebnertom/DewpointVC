# DewpointVC
Dewpoint Ventilation Control software using Raspberry Pi 3b+.
Temperature and Humidity is measured inside and outside using DHT22 sensors and a fan that is controlled via
a solid state relais.
The fan, blowing air from outside into the cellar, is controlled in such a way that the humidity of the cellar
is minimized.

## development / debugging od code on raspberry pi

You can launch a docker-container on the raspberry pi that offers a ssh-server that can be used for
code execution / debugging using PyCharm.
Therefore, you need to do the following steps on your raspberry pi:
1. checkout this repository on the raspberry pi
2. specify your public key of your development machine in [authorized_keys.pub](docker%2Fdev_ssh%2Fauthorized_keys.pub)
3. launch the script [run_ssh_for_debugging.sh](scripts%2Frun_ssh_for_debugging.sh).

To connect via Pycharm, add a New Interpreter: In the project settings or preferences,
configure a new Python interpreter. This interpreter will be used to run your Python code within the Docker container.

1. first try if SSH connection works by connecting to the raspberry pi ssh server using a terminal. 
2. select SSH Interpreter
3. new server connection: specify host / port (1022) of raspberry pi. username root.
4. select system interpreter
