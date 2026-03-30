# routes.py
from flask import request, jsonify, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .auth.auth import register_user, login_user
from .auth.validators import validate_actuator_control, ValidationError
from .services.sensor_generator import generate_test_data
from .database.db_connection import execute_query
from datetime import datetime, timedelta
from .config import Config

def register_routes(app):
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

    # ============================================
    # АУТЕНТИФИКАЦИЯ
    # ============================================
    @app.route('/api/auth/register', methods=['POST'])
    @limiter.limit("5 per minute")
    def register():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "No data provided"}), 400
            result = register_user(data['username'], data['password'], data['email'])
            return jsonify(result), 201 if result['success'] else 400
        except Exception as e:
            print(e)
            return jsonify({"success": False, "message": "Registration failed"}), 500

    @app.route('/api/auth/login', methods=['POST'])
    @limiter.limit("10 per minute")
    def login():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "No data provided"}), 400

            result = login_user(data['username'], data['password'])
            return jsonify(result), 200 if result['success'] else 401
        except Exception as e:
            return jsonify({"success": False, "message": "Login failed"}), 500

    # ============================================
    # ДАННЫЕ С ДАТЧИКОВ
    # ============================================
    @app.route('/api/sensors/current', methods=['GET'])
    def get_current_sensors():
        try:
            reading = execute_query(
                'SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 1',
                fetch_one=True
            )

            if reading:
                return jsonify({
                    "timestamp": reading['timestamp'],
                    "sensors": {
                        "temperature": {"value": reading['temperature'], "unit": "°C"},
                        "humidity": {"value": reading['humidity'], "unit": "%"},
                        "co2": {"value": reading['co2'], "unit": "ppm"},
                        "voc": {"value": reading['voc'], "unit": "ppb"},
                        "pm2_5": {"value": reading['pm2_5'], "unit": "µg/m³"},
                        "pm10": {"value": reading['pm10'], "unit": "µg/m³"}
                    }
                })
            else:
                test_data = generate_test_data()
                return jsonify({
                    "timestamp": datetime.now().isoformat(),
                    "sensors": {
                        "temperature": {"value": test_data["temperature"], "unit": "°C"},
                        "humidity": {"value": test_data["humidity"], "unit": "%"},
                        "co2": {"value": test_data["co2"], "unit": "ppm"},
                        "voc": {"value": test_data["voc"], "unit": "ppb"},
                        "pm2_5": {"value": test_data["pm2_5"], "unit": "µg/m³"},
                        "pm10": {"value": test_data["pm10"], "unit": "µg/m³"}
                    },
                    "message": "No historical data, generated test data"
                })
        except Exception as e:
            return jsonify({"success": False, "message": "Failed to get sensor data"}), 500

    @app.route('/api/sensors/history', methods=['GET'])
    def get_sensor_history():
        try:
            hours = request.args.get('hours', 24, type=int)
            readings = execute_query(
                'SELECT * FROM sensor_readings WHERE timestamp > ? ORDER BY timestamp ASC',
                ((datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S'),),
                fetch_all=True
            )

            return jsonify({
                "period": f"last_{hours}_hours",
                "count": len(readings),
                "data": [
                    {
                        "timestamp": r['timestamp'],
                        "temperature": r['temperature'],
                        "humidity": r['humidity'],
                        "co2": r['co2'],
                        "voc": r['voc'],
                        "pm2_5": r['pm2_5'],
                        "pm10": r['pm10']
                    } for r in readings
                ]
            })
        except Exception as e:
            return jsonify({"success": False, "message": "Failed to get sensor history"}), 500

    @app.route('/api/sensors/statistics', methods=['GET'])
    def get_sensor_statistics():
        try:
            hours = request.args.get('hours', 24, type=int)
            result = execute_query(
                '''
                SELECT COUNT(*), AVG(temperature), MIN(temperature), MAX(temperature),
                       AVG(humidity), AVG(co2), AVG(voc), AVG(pm2_5), AVG(pm10)
                FROM sensor_readings
                WHERE timestamp > ?
                ''',
                ((datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S'),),
                fetch_one=True
            )

            if result and result.get('COUNT(*)', 0) > 0:
                return jsonify({
                    "period_hours": hours,
                    "readings_count": result['COUNT(*)'],
                    "temperature": {"avg": round(result['AVG(temperature)'],1), "min": round(result['MIN(temperature)'],1), "max": round(result['MAX(temperature)'],1)},
                    "humidity": {"avg": round(result['AVG(humidity)'],1)},
                    "co2": {"avg": round(result['AVG(co2)'])},
                    "voc": {"avg": round(result['AVG(voc)'])},
                    "pm2_5": {"avg": round(result['AVG(pm2_5)'])},
                    "pm10": {"avg": round(result['AVG(pm10)'])}
                })
            else:
                return jsonify({
                    "period_hours": hours,
                    "readings_count": 0,
                    "temperature": {"avg": 0, "min": 0, "max": 0},
                    "humidity": {"avg": 0},
                    "co2": {"avg": 0},
                    "voc": {"avg": 0},
                    "pm2_5": {"avg": 0},
                    "pm10": {"avg": 0}
                })
        except Exception as e:
            return jsonify({"success": False, "message": "Failed to get sensor statistics"}), 500

    # ============================================
    # УПРАВЛЕНИЕ АКТУАТОРАМИ
    # ============================================
    @app.route('/api/actuators/status', methods=['GET'])
    def get_actuators_status():
        try:
            actuators = execute_query(
                "SELECT name, type, state, updated_at FROM actuators",
                fetch_all=True
            )

            return jsonify({
                "actuators": {a['name']: {"type": a['type'], "state": a['state'], "updated_at": a['updated_at']} for a in actuators}
            })
        except Exception as e:
            return jsonify({"success": False, "message": "Failed to get actuator status"}), 500

    @app.route('/api/actuators/control', methods=['POST'])
    @limiter.limit("20 per minute")
    def control_actuator():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "No data provided"}), 400

            # Validate input
            validated_data = validate_actuator_control(data)
            device_name = validated_data['device']
            action = validated_data['action']

            # Get current state
            current_device = execute_query(
                "SELECT state FROM actuators WHERE name = ?",
                (device_name,),
                fetch_one=True
            )

            if not current_device:
                return jsonify({"success": False, "message": "Device not found"}), 404

            # Calculate new state safely
            if action == 'toggle':
                new_state = 'off' if current_device['state'] == 'on' else 'on'
            elif action == 'turn_on':
                new_state = 'on'
            elif action == 'turn_off':
                new_state = 'off'
            else:
                return jsonify({"success": False, "message": "Invalid action"}), 400

            # Update state
            execute_query(
                "UPDATE actuators SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (new_state, device_name)
            )

            return jsonify({
                "success": True,
                "device": device_name,
                "new_state": new_state,
                "message": f"Device {device_name} turned {new_state}"
            })
        except ValidationError as e:
            return jsonify({"success": False, "message": "Validation failed", "errors": str(e)}), 400
        except Exception as e:
            return jsonify({"success": False, "message": "Failed to control actuator"}), 500

    # ============================================
    # УВЕДОМЛЕНИЯ
    # ============================================
    @app.route('/api/notifications', methods=['GET'])
    def get_notifications():
        try:
            user_id = 1  # тестовый пользователь
            notifications = execute_query(
                'SELECT id,type,message,timestamp,read FROM notifications WHERE user_id=? ORDER BY timestamp DESC LIMIT 50',
                (user_id,),
                fetch_all=True
            )

            return jsonify({"notifications":[{"id":n['id'],"type":n['type'],"message":n['message'],"timestamp":n['timestamp'],"read":bool(n['read'])} for n in notifications]})
        except Exception as e:
            return jsonify({"success": False, "message": "Failed to get notifications"}), 500

    # ============================================
    # УПРАВЛЕНИЕ УСТРОЙСТВАМИ
    # ============================================
    @app.route('/api/devices/list', methods=['GET'])
    def get_devices_list():
        try:
            actuators = execute_query(
                'SELECT name,type,state,id FROM actuators',
                fetch_all=True
            )

            devices = [{"id":a['id'],"name":a['name'],"type":"actuator","subtype":a['type'],"state":a['state']} for a in actuators]
            return jsonify({"devices": devices, "count": len(devices)})
        except Exception as e:
            return jsonify({"success": False, "message": "Failed to get devices list"}), 500

    # ============================================
    # ВЕБ-ИНТЕРФЕЙС
    # ============================================
    @app.route('/')
    def index():
        return render_template('dashboard.html')
