# routes.py
import sys
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import sqlite3
from datetime import datetime, timedelta
import threading
import time

# Добавляем родительскую папку в путь Python
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Импорт локальных модулей
from domain import database
from auth.auth import register_user, login_user
from domain.sensors import (
    print_devices_info,
    generate_test_data,
    check_thresholds_and_notify
)

# ЕДИНСТВЕННОЕ определение приложения
app = Flask(__name__, template_folder='../templates')
CORS(app)
app.config['JWT_SECRET_KEY'] = 'climate-system-secret-key-2026'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
jwt = JWTManager(app)

# Инициализация БД при запуске
database.init_db()


# Функция для получения пути к БД
def get_db_path():
    return os.path.join(parent_dir, 'climate_system.db')


# Вывод информации об устройствах при запуске сервера
print("\n" + "=" * 70)
print("СИСТЕМА АНАЛИЗА МИКРОКЛИМАТА - ЗАПУСК СЕРВЕРА")
print("=" * 70)
print_devices_info()


# ============================================
# АУТЕНТИФИКАЦИЯ
# ============================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    result = register_user(data['username'], data['password'], data['email'])
    return jsonify(result), 201 if result['success'] else 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"success": False, "message": "Missing username or password"}), 400

    result = login_user(data['username'], data['password'])
    return jsonify(result), 200 if result['success'] else 401


# ============================================
# ДАННЫЕ С ДАТЧИКОВ
# ============================================

@app.route('/api/sensors/current', methods=['GET'])
def get_current_sensors():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM sensor_readings 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''')
    reading = cursor.fetchone()
    conn.close()

    if reading:
        return jsonify({
            "timestamp": reading[1],
            "sensors": {
                "temperature": {"value": reading[2], "unit": "°C"},
                "humidity": {"value": reading[3], "unit": "%"},
                "co2": {"value": reading[4], "unit": "ppm"},
                "voc": {"value": reading[5], "unit": "ppb"},
                "pm2_5": {"value": reading[6], "unit": "µg/m³"},
                "pm10": {"value": reading[7], "unit": "µg/m³"}
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


@app.route('/api/sensors/history', methods=['GET'])
def get_sensor_history():
    hours = request.args.get('hours', 24, type=int)
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # ПРАВИЛЬНЫЙ ФОРМАТ ВРЕМЕНИ ДЛЯ SQLITE
    time_threshold = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        SELECT * FROM sensor_readings 
        WHERE timestamp > ? 
        ORDER BY timestamp ASC
    ''', (time_threshold,))

    readings = cursor.fetchall()
    conn.close()

    return jsonify({
        "period": f"last_{hours}_hours",
        "count": len(readings),
        "data": [
            {
                "timestamp": r[1],
                "temperature": r[2],
                "humidity": r[3],
                "co2": r[4],
                "voc": r[5],
                "pm2_5": r[6],
                "pm10": r[7]
            } for r in readings
        ]
    })


@app.route('/api/sensors/statistics', methods=['GET'])
def get_sensor_statistics():
    """Получение статистики показаний за период"""
    hours = request.args.get('hours', 24, type=int)
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # ПРАВИЛЬНЫЙ ФОРМАТ ВРЕМЕНИ ДЛЯ SQLITE
    time_threshold = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        SELECT 
            COUNT(*) as count,
            AVG(temperature) as avg_temp,
            MIN(temperature) as min_temp,
            MAX(temperature) as max_temp,
            AVG(humidity) as avg_hum,
            AVG(co2) as avg_co2,
            AVG(voc) as avg_voc,
            AVG(pm2_5) as avg_pm2_5,
            AVG(pm10) as avg_pm10
        FROM sensor_readings
        WHERE timestamp > ?
    ''', (time_threshold,))

    result = cursor.fetchone()
    conn.close()

    if result and result[0] > 0:
        return jsonify({
            "period_hours": hours,
            "readings_count": result[0],
            "temperature": {
                "avg": round(result[1], 1) if result[1] else 0,
                "min": round(result[2], 1) if result[2] else 0,
                "max": round(result[3], 1) if result[3] else 0
            },
            "humidity": {"avg": round(result[4], 1) if result[4] else 0},
            "co2": {"avg": round(result[5]) if result[5] else 0},
            "voc": {"avg": round(result[6]) if result[6] else 0},
            "pm2_5": {"avg": round(result[7]) if result[7] else 0},
            "pm10": {"avg": round(result[8]) if result[8] else 0}
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


# ============================================
# УПРАВЛЕНИЕ АКТУАТОРАМИ
# ============================================

@app.route('/api/actuators/status', methods=['GET'])
def get_actuators_status():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute("SELECT name, type, state, updated_at FROM actuators")
    actuators = cursor.fetchall()
    conn.close()

    return jsonify({
        "actuators": {
            a[0]: {"type": a[1], "state": a[2], "updated_at": a[3]}
            for a in actuators
        }
    })


@app.route('/api/actuators/control', methods=['POST'])
def control_actuator():
    data = request.get_json()
    if not data or 'device' not in data or 'action' not in data:
        return jsonify({"success": False, "message": "Missing device or action"}), 400

    device_name = data['device']
    action = data['action']

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute("SELECT state FROM actuators WHERE name = ?", (device_name,))
    current_state = cursor.fetchone()

    if not current_state:
        return jsonify({"success": False, "message": "Device not found"}), 404

    if action == 'toggle':
        new_state = 'off' if current_state[0] == 'on' else 'on'
    else:
        new_state = 'on' if action == 'turn_on' else 'off'

    cursor.execute(
        "UPDATE actuators SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
        (new_state, device_name)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "device": device_name,
        "new_state": new_state,
        "message": f"Device {device_name} turned {new_state}"
    })


# ============================================
# УВЕДОМЛЕНИЯ
# ============================================

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Получение уведомлений пользователя"""
    user_id = 1  # Тестовый пользователь

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT OR IGNORE INTO users (username, password, email) VALUES (?, ?, ?)",
            ('testuser', 'pbkdf2:sha256:260000$dummy$password', 'test@example.com')
        )
        conn.commit()

    cursor.execute('''
        SELECT id, type, message, timestamp, read 
        FROM notifications 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''', (user_id,))

    notifications = cursor.fetchall()
    conn.close()

    return jsonify({
        "notifications": [
            {
                "id": n[0],
                "type": n[1],
                "message": n[2],
                "timestamp": n[3],
                "read": bool(n[4])
            } for n in notifications
        ]
    })


# ============================================
# УПРАВЛЕНИЕ УСТРОЙСТВАМИ
# ============================================

@app.route('/api/devices/list', methods=['GET'])
def get_devices_list():
    """Получение списка всех устройств"""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('SELECT name, type, state, id FROM actuators')
    actuators = cursor.fetchall()
    conn.close()

    devices = []
    for actuator in actuators:
        devices.append({
            "id": actuator[3],
            "name": actuator[0],
            "type": "actuator",
            "subtype": actuator[1],
            "state": actuator[2]
        })

    return jsonify({
        "devices": devices,
        "count": len(devices)
    })


# ============================================
# ВЕБ-ИНТЕРФЕЙС
# ============================================

@app.route('/')
def index():
    return render_template('dashboard.html')


# ============================================
# ФОНОВЫЙ ПОТОК ГЕНЕРАЦИИ ДАННЫХ
# ============================================

def background_data_generator():
    """Фоновый поток для генерации тестовых данных"""
    print("\n" + "=" * 70)
    print("ЗАПУСК ФОНОВОГО ГЕНЕРАТОРА ДАННЫХ")
    print("=" * 70)
    print("Частота генерации: 1 раз в 5 секунд")
    print("=" * 70)

    while True:
        try:
            generate_test_data()
            check_thresholds_and_notify()
            time.sleep(5)
        except Exception as e:
            print(f"❌ Ошибка в фоновом потоке: {e}")
            time.sleep(5)


# Запуск фонового потока
threading.Thread(target=background_data_generator, daemon=True).start()

# ============================================
# ЗАПУСК СЕРВЕРА
# ============================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("СЕРВЕР ЗАПУЩЕН НА: http://localhost:5000")
    print("=" * 70)
    print("Доступные эндпоинты:")
    print("  GET  /                           - Веб-интерфейс")
    print("  POST /api/auth/register          - Регистрация")
    print("  POST /api/auth/login             - Вход")
    print("  GET  /api/sensors/current        - Текущие показания")
    print("  GET  /api/sensors/history        - История показаний")
    print("  GET  /api/sensors/statistics     - Статистика")
    print("  GET  /api/actuators/status       - Статус устройств")
    print("  POST /api/actuators/control      - Управление устройствами")
    print("  GET  /api/notifications          - Уведомления")
    print("  GET  /api/devices/list           - Список устройств")
    print("=" * 70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)