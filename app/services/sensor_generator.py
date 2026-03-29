# sensor_generator.py
import sqlite3
import time
import random
from datetime import datetime


def generate_test_data():
    from app.domain.devices import DEVICE_IDS
    """Генерация тестовых данных (без сохранения в БД!)"""

    data = {
        "temperature": round(random.uniform(20.0, 23.0), 1),
        "humidity": random.randint(40, 55),
        "co2": random.randint(600, 900),
        "voc": random.randint(100, 300),
        "pm2_5": random.randint(10, 30),
        "pm10": random.randint(15, 40)
    }
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{timestamp}] ПОКАЗАНИЯ ДАТЧИКОВ:")
    print(f"  Температура: {data['temperature']} °C (ID: {DEVICE_IDS['temperature_sensor'][:8]}...)")
    print(f"  Влажность: {data['humidity']} % (ID: {DEVICE_IDS['humidity_sensor'][:8]}...)")
    print(f"  CO₂: {data['co2']} ppm (ID: {DEVICE_IDS['co2_sensor'][:8]}...)")
    print(f"  ЛОС: {data['voc']} ppb (ID: {DEVICE_IDS['voc_sensor'][:8]}...)")
    print(f"  PM2.5: {data['pm2_5']} µg/m³ (ID: {DEVICE_IDS['pm25_sensor'][:8]}...)")
    print(f"  PM10: {data['pm10']} µg/m³ (ID: {DEVICE_IDS['pm10_sensor'][:8]}...)")

    return data
