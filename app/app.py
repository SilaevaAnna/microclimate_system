# app.py
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

jwt = JWTManager()

def create_app():
    app = Flask(__name__, template_folder='../templates')

    app.config['JWT_SECRET_KEY'] = 'climate-system-secret-key-2026'
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'

    CORS(app)
    jwt.init_app(app)

    from .routes import register_routes
    register_routes(app)

    return app

import threading
import time
from app.services.sensors import generate_test_data, check_thresholds_and_notify

def start_background_thread():
    def background_data_generator():
        while True:
            try:
                generate_test_data()
                check_thresholds_and_notify()
                time.sleep(5)
            except Exception as e:
                print(f"❌ Ошибка в фоновом потоке: {e}")
                time.sleep(5)

    threading.Thread(target=background_data_generator, daemon=True).start()


app = create_app()
start_background_thread()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)