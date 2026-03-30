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
        import sqlite3
        import os
        
        # Get correct database path - same as used by db_connection
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'microclimate_system', 'climate_system.db')
        
        while True:
            try:
                # Generate test data
                data = generate_test_data()
                
                # Save data to database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(
                    '''INSERT INTO sensor_readings (temperature, humidity, co2, voc, pm2_5, pm10) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (data['temperature'], data['humidity'], data['co2'], 
                     data['voc'], data['pm2_5'], data['pm10'])
                )
                conn.commit()
                conn.close()
                print(f"Data saved to database: {data}")
                
                # Check thresholds and notify
                check_thresholds_and_notify()
                
                time.sleep(5)
            except Exception as e:
                print(f"ERROR in background thread: {e}")
                print(f"Database path: {db_path}")
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
