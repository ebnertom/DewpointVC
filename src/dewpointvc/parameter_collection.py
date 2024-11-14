import json
import os
import logging

class ParameterCollection:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path

        # Default parameters
        self.parameters = {
            "dewpoint_on_threshold": 4.0,
            "dewpoint_off_threshold": 3.0,
            "min_on_duration": 60,
            "max_on_duration": 5 * 60,
            "min_off_duration": 4 * 60 * 60,
            "min_inside_temperature": 10,
            "min_outside_temperature": -2,
        }
        self.log = logging.getLogger(__name__)
        # Load parameters from file if it exists, otherwise use default
        self.load_parameters()

    def load_parameters(self):
        """Loads parameters from the JSON file if it exists."""
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'r') as file:
                self.parameters.update(json.load(file))

    def save_parameters(self):
        """Saves current parameters to the JSON file."""
        with open(self.config_file_path, 'w') as file:
            json.dump(self.parameters, file, indent=4)

    # Getters
    def get_param(self, param):
        """Get the value of a parameter."""
        return self.parameters.get(param, None)

    # Setters
    def set_param(self, param, value):
        """Set the value of a parameter and save it."""
        self.parameters[param] = value
        self.save_parameters()