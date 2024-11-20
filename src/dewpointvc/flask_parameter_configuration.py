import logging
import os
import threading

from flask import Flask, render_template, request, redirect, url_for, flash

from dewpointvc.parameter_collection import ParameterCollection


class FlaskParameterConfiguration:
    def __init__(self, config_service):
        self.config_service = config_service
        self.app = Flask(__name__,
                         template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
        self.setup_routes()
        self.app.secret_key = "Eejeich6eT6hooMu"  # Required for flash messages
        self.logger = logging.getLogger(__name__)

    def setup_routes(self):
        """Set up Flask routes for the web interface."""
        @self.app.route('/')
        def index():
            # Pass parameters to the template for display
            parameters = self.config_service.parameters
            self.logger.debug("Rendering index page with parameters: %s", parameters)
            return render_template('index.html', parameters=parameters)

        @self.app.route('/update', methods=['POST'])
        def update_params():
            # Update all parameters based on form data
            for param, value in request.form.items():
                default_value = self.config_service.get_param(param)
                try:
                    if isinstance(default_value, bool):
                        value = value.lower() in ["true", "1"]
                    elif isinstance(default_value, int):
                        value = int(value)
                    elif isinstance(default_value, float):
                        value = float(value)

                    if value != default_value:
                        self.logger.info(
                            "Updated parameter '%s' from: %s to: %s", param, default_value, value
                        )
                    # Set the parameter with the updated value
                    self.config_service.set_param(param, value)
                    self.logger.info("Updated parameter '%s' to: %s", param, value)
                except (ValueError, TypeError):
                    flash(f"Invalid value for parameter '{param}': {value}", 'error')
                    # return redirect(url_for('index'))
            return redirect(url_for('index'))

    def run(self):
        """Run the Flask app in the main thread (blocking)."""
        self.logger.info("Starting Flask app in main thread.")
        self.app.run(host='0.0.0.0', port=5000, debug=False)

    def start_background(self):
        """Run the Flask app in a background thread."""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        self.logger.info("Flask server started in background.")


# To start the Flask web server:
if __name__ == "__main__":
    p = ParameterCollection('params.json')
    config_app = FlaskParameterConfiguration(p)
    config_app.run()