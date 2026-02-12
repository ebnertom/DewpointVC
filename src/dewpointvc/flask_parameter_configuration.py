import logging
import os
import threading
import time
from collections import deque
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from dewpointvc.parameter_collection import ParameterCollection


class InMemoryLogHandler(logging.Handler):
    """Custom log handler that stores log records in memory."""
    def __init__(self, max_logs=1000):
        super().__init__()
        self.logs = deque(maxlen=max_logs)
        self.__lock = threading.Lock()

    def emit(self, record):
        with self.__lock:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
                'level': record.levelname,
                'name': record.name,
                'message': self.format(record)
            }
            self.logs.append(log_entry)

    def get_logs(self, limit=None):
        with self.__lock:
            if limit:
                return list(self.logs)[-limit:]
            return list(self.logs)


class FlaskParameterConfiguration:
    def __init__(self, config_service):
        self.config_service = config_service
        self.app = Flask(__name__,
                         template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

        # Set up in-memory log handler
        self.log_handler = InMemoryLogHandler(max_logs=1000)
        self.log_handler.setLevel(logging.DEBUG)  # Capture all log levels
        self.log_handler.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().info("InMemoryLogHandler installed")

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

        @self.app.route('/logs')
        def logs():
            """Render the logs viewer page."""
            return render_template('logs.html')

        @self.app.route('/api/logs')
        def api_logs():
            """API endpoint to fetch logs."""
            limit = request.args.get('limit', default=100, type=int)
            logs = self.log_handler.get_logs(limit=limit)
            return jsonify(logs)

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
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    p = ParameterCollection('params.json')
    config_app = FlaskParameterConfiguration(p)
    config_app.start_background()

    while True:
        logging.info('whoop')
        time.sleep(1)
