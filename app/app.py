# app.py
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.services.notification_service import check_thresholds_and_notify
from app.services.sensor_generator import generate_test_data
from .config import config
import threading
import time

jwt = JWTManager()


def create_app(config_name='default'):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(config[config_name])

    CORS(app, origins=app.config['CORS_ORIGINS'])
    jwt.init_app(app)

    from .routes import register_routes
    register_routes(app)

    return app


def start_background_thread():
    def background_data_generator():
        while True:
            try:
                generate_test_data()
                check_thresholds_and_notify()
                time.sleep(5)
            except Exception as e:
                print(f"ERROR in background thread: {e}")
                time.sleep(5)

    threading.Thread(target=background_data_generator, daemon=True).start()


if __name__ == '__main__':
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)
    start_background_thread()
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )
