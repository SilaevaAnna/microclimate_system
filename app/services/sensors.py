# sensors.py
import sqlite3
from datetime import datetime
import random
import uuid
import time


# Уникальные идентификаторы для каждого датчика (генерируются один раз)
DEVICE_IDS = {
    'temperature_sensor': str(uuid.uuid4()),
    'humidity_sensor': str(uuid.uuid4()),
    'co2_sensor': str(uuid.uuid4()),
    'voc_sensor': str(uuid.uuid4()),
    'pm25_sensor': str(uuid.uuid4()),
    'pm10_sensor': str(uuid.uuid4()),
    'humidifier': str(uuid.uuid4()),
    'fan': str(uuid.uuid4()),
    'heater': str(uuid.uuid4())
}

# Описание устройств
DEVICES_INFO = {
    'temperature_sensor': {
        'name': 'Датчик температуры',
        'type': 'sensor',
        'model': 'SHT3x / BME280',
        'range': {'min': -40, 'max': 85, 'unit': '°C'},
        'optimal': {'min': 18, 'max': 24, 'unit': '°C'},
        'critical': {'min': 10, 'max': 30, 'unit': '°C'}
    },
    'humidity_sensor': {
        'name': 'Датчик влажности',
        'type': 'sensor',
        'model': 'SHT3x / BME280',
        'range': {'min': 0, 'max': 100, 'unit': '%'},
        'optimal': {'min': 30, 'max': 60, 'unit': '%'},
        'critical': {'min': 20, 'max': 70, 'unit': '%'}
    },
    'co2_sensor': {
        'name': 'Датчик углекислого газа',
        'type': 'sensor',
        'model': 'MH-Z19B',
        'range': {'min': 0, 'max': 5000, 'unit': 'ppm'},
        'optimal': {'min': 600, 'max': 800, 'unit': 'ppm'},
        'critical': {'min': 800, 'max': 1000, 'unit': 'ppm'},
        'danger': {'min': 1000, 'max': 5000, 'unit': 'ppm'}
    },
    'voc_sensor': {
        'name': 'Датчик летучих органических соединений',
        'type': 'sensor',
        'model': 'SGP30',
        'range': {'min': 0, 'max': 60000, 'unit': 'ppb'},
        'optimal': {'min': 0, 'max': 220, 'unit': 'ppb'},
        'critical': {'min': 220, 'max': 660, 'unit': 'ppb'},
        'danger': {'min': 660, 'max': 60000, 'unit': 'ppb'}
    },
    'pm25_sensor': {
        'name': 'Датчик твёрдых частиц PM2.5',
        'type': 'sensor',
        'model': 'PMS5003',
        'range': {'min': 0, 'max': 1000, 'unit': 'µg/m³'},
        'optimal': {'min': 0, 'max': 15, 'unit': 'µg/m³'},
        'critical': {'min': 15, 'max': 35, 'unit': 'µg/m³'},
        'danger': {'min': 35, 'max': 1000, 'unit': 'µg/m³'}
    },
    'pm10_sensor': {
        'name': 'Датчик твёрдых частиц PM10',
        'type': 'sensor',
        'model': 'PMS5003',
        'range': {'min': 0, 'max': 1000, 'unit': 'µg/m³'},
        'optimal': {'min': 0, 'max': 25, 'unit': 'µg/m³'},
        'critical': {'min': 25, 'max': 50, 'unit': 'µg/m³'},
        'danger': {'min': 50, 'max': 1000, 'unit': 'µg/m³'}
    },
    'humidifier': {
        'name': 'Увлажнитель воздуха',
        'type': 'actuator',
        'model': 'Релейный модуль',
        'states': ['off', 'on'],
        'default': 'off'
    },
    'fan': {
        'name': 'Вентилятор',
        'type': 'actuator',
        'model': 'Релейный модуль',
        'states': ['off', 'on'],
        'default': 'off'
    },
    'heater': {
        'name': 'Обогреватель',
        'type': 'actuator',
        'model': 'Релейный модуль',
        'states': ['off', 'on'],
        'default': 'off'
    }
}


def get_device_info(device_name):
    """Получение информации об устройстве"""
    info = DEVICES_INFO.get(device_name, {})
    info['id'] = DEVICE_IDS.get(device_name, 'unknown')
    return info


def print_devices_info():
    """Вывод информации обо всех устройствах в консоль"""
    print("=" * 70)
    print("ИНФОРМАЦИЯ ОБ УСТРОЙСТВАХ СИСТЕМЫ МИКРОКЛИМАТА")
    print("=" * 70)

    print("\n--- ДАТЧИКИ ---")
    for name, info in DEVICES_INFO.items():
        if info.get('type') == 'sensor':
            print(f"\n{name.upper()}")
            print(f"  Название: {info['name']}")
            print(f"  Модель: {info['model']}")
            print(f"  ID: {DEVICE_IDS[name]}")
            print(f"  Диапазон: {info['range']['min']}–{info['range']['max']} {info['range']['unit']}")
            print(f"  Оптимально: {info['optimal']['min']}–{info['optimal']['max']} {info['optimal']['unit']}")
            print(f"  Критично: {info['critical']['min']}–{info['critical']['max']} {info['critical']['unit']}")
            if 'danger' in info:
                print(f"  Опасно: >{info['danger']['min']} {info['danger']['unit']}")

    print("\n--- АКТУАТОРЫ ---")
    for name, info in DEVICES_INFO.items():
        if info.get('type') == 'actuator':
            print(f"\n{name.upper()}")
            print(f"  Название: {info['name']}")
            print(f"  Модель: {info['model']}")
            print(f"  ID: {DEVICE_IDS[name]}")
            print(f"  Состояния: {', '.join(info['states'])}")
            print(f"  По умолчанию: {info['default']}")

    print("\n" + "=" * 70)


def save_sensor_reading(temperature, humidity, co2, voc, pm2_5, pm10):
    """Сохранение показаний датчиков в базу данных"""
    conn = sqlite3.connect('../../climate_system.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO sensor_readings 
        (temperature, humidity, co2, voc, pm2_5, pm10)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (temperature, humidity, co2, voc, pm2_5, pm10))

    conn.commit()
    conn.close()
    return True


def generate_test_data():
    """Генерация тестовых данных для демонстрации"""
    # Генерация случайных значений в допустимых диапазонах
    temp = round(random.uniform(20.0, 23.0), 1)
    humidity = random.randint(40, 55)
    co2 = random.randint(600, 900)
    voc = random.randint(100, 300)
    pm2_5 = random.randint(10, 30)
    pm10 = random.randint(15, 40)

    # Сохранение в базу данных
    save_sensor_reading(temp, humidity, co2, voc, pm2_5, pm10)

    # Вывод в консоль для демонстрации работоспособности
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[{timestamp}] ПОКАЗАНИЯ ДАТЧИКОВ:")
    print(f"  Температура: {temp} °C (ID: {DEVICE_IDS['temperature_sensor'][:8]}...)")
    print(f"  Влажность: {humidity} % (ID: {DEVICE_IDS['humidity_sensor'][:8]}...)")
    print(f"  CO₂: {co2} ppm (ID: {DEVICE_IDS['co2_sensor'][:8]}...)")
    print(f"  ЛОС: {voc} ppb (ID: {DEVICE_IDS['voc_sensor'][:8]}...)")
    print(f"  PM2.5: {pm2_5} µg/m³ (ID: {DEVICE_IDS['pm25_sensor'][:8]}...)")
    print(f"  PM10: {pm10} µg/m³ (ID: {DEVICE_IDS['pm10_sensor'][:8]}...)")

    return {
        "temperature": temp,
        "humidity": humidity,
        "co2": co2,
        "voc": voc,
        "pm2_5": pm2_5,
        "pm10": pm10
    }


def automatic_control_based_on_sensors(temp, humidity, co2):
    """
    Автоматическое управление актуаторами на основе показаний датчиков
    Схема соответствия:
    - Температура < 18°C → включить обогреватель
    - Температура > 26°C → включить вентилятор
    - Влажность < 30% → включить увлажнитель
    - Влажность > 60% → включить вентилятор
    - СО2 > 1000 ppm → включить вентилятор
    """
    actions = []

    conn = sqlite3.connect('../../climate_system.db')
    cursor = conn.cursor()

    # Проверка температуры
    if temp < 18:
        actions.append(('heater', 'turn_on', f'Температура низкая: {temp}°C'))
    elif temp > 26:
        actions.append(('fan', 'turn_on', f'Температура высокая: {temp}°C'))
    else:
        actions.append(('heater', 'turn_off', ''))
        actions.append(('fan', 'turn_off', ''))

    # Проверка влажности
    if humidity < 30:
        actions.append(('humidifier', 'turn_on', f'Влажность низкая: {humidity}%'))
    elif humidity > 60:
        actions.append(('fan', 'turn_on', f'Влажность высокая: {humidity}%'))
    else:
        actions.append(('humidifier', 'turn_off', ''))

    # Проверка СО2
    if co2 > 1000:
        actions.append(('fan', 'turn_on', f'СО2 критический: {co2} ppm'))

    # Применение действий
    for device_name, action, reason in actions:
        if action == 'turn_on':
            cursor.execute(
                "UPDATE actuators SET state = 'on', updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (device_name,)
            )
            if reason:
                print(f"  ⚙️  {device_name.upper()}: ВКЛЮЧЁН ({reason})")
        elif action == 'turn_off':
            cursor.execute(
                "UPDATE actuators SET state = 'off', updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (device_name,)
            )

    conn.commit()
    conn.close()

    return actions


def check_thresholds_and_notify():
    """Проверка пороговых значений и создание уведомлений"""
    conn = sqlite3.connect('../../climate_system.db')
    cursor = conn.cursor()

    # Получаем последнее измерение
    cursor.execute('''
        SELECT temperature, humidity, co2, voc, pm2_5, pm10 
        FROM sensor_readings 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''')
    reading = cursor.fetchone()

    if reading:
        temp, humidity, co2, voc, pm2_5, pm10 = reading
        notifications = []

        # Проверка температуры
        if temp < 18:
            notifications.append(("warning", f"Низкая температура: {temp}°C (норма: 18-24°С)"))
        elif temp > 26:
            notifications.append(("warning", f"Высокая температура: {temp}°C (норма: 18-24°С)"))

        # Проверка влажности
        if humidity < 30:
            notifications.append(("warning", f"Низкая влажность: {humidity}% (норма: 30-60%)"))
        elif humidity > 60:
            notifications.append(("warning", f"Высокая влажность: {humidity}% (норма: 30-60%)"))

        # Проверка СО2
        if co2 > 1000:
            notifications.append(("alert", f"КРИТИЧЕСКИЙ уровень СО2: {co2} ppm (норма: 600-800 ppm)"))
        elif co2 > 800:
            notifications.append(("warning", f"Повышенный уровень СО2: {co2} ppm (норма: 600-800 ppm)"))

        # Проверка ЛОС (VOC)
        if voc > 500:
            notifications.append(("alert", f"Высокий уровень ЛОС: {voc} ppb"))
        elif voc > 300:
            notifications.append(("warning", f"Повышенный уровень ЛОС: {voc} ppb"))

        # Проверка пыли PM2.5
        if pm2_5 > 35:
            notifications.append(("alert", f"Высокий уровень пыли PM2.5: {pm2_5} µg/m³ (норма: 0-15 µg/m³)"))
        elif pm2_5 > 15:
            notifications.append(("warning", f"Повышенный уровень пыли PM2.5: {pm2_5} µg/m³"))

        # Проверка пыли PM10
        if pm10 > 50:
            notifications.append(("alert", f"Высокий уровень пыли PM10: {pm10} µg/m³ (норма: 0-25 µg/m³)"))
        elif pm10 > 25:
            notifications.append(("warning", f"Повышенный уровень пыли PM10: {pm10} µg/m³"))

        # Сохранение уведомлений
        if notifications:
            cursor.execute("SELECT id FROM users LIMIT 1")
            user = cursor.fetchone()
            if user:
                for notif_type, message in notifications:
                    cursor.execute('''
                        INSERT INTO notifications (user_id, type, message)
                        VALUES (?, ?, ?)
                    ''', (user[0], notif_type, message))
                    print(f"  УВЕДОМЛЕНИЕ [{notif_type.upper()}]: {message}")
                conn.commit()

    conn.close()


def background_data_generator():
    """Фоновый поток для генерации тестовых данных"""
    print("\n" + "=" * 70)
    print("ЗАПУСК ФОНОВОГО ГЕНЕРАТОРА ДАННЫХ")
    print("=" * 70)
    print("Частота генерации: 1 раз в 5 секунд")
    print("Автоматическое управление: ВКЛЮЧЕНО")
    print("Проверка порогов: ВКЛЮЧЕНА")
    print("=" * 70)

    # Вывод информации об устройствах
    print_devices_info()

    print("\n" + "=" * 70)
    print("НАЧАЛО ГЕНЕРАЦИИ ДАННЫХ...")
    print("=" * 70)

    while True:
        try:
            # Генерация данных
            data = generate_test_data()

            # Автоматическое управление актуаторами
            automatic_control_based_on_sensors(
                data['temperature'],
                data['humidity'],
                data['co2']
            )

            # Проверка порогов и создание уведомлений
            check_thresholds_and_notify()

            # Пауза 5 секунд
            time.sleep(5)

        except Exception as e:
            print(f"\nОшибка в фоновом потоке: {e}")
            time.sleep(5)