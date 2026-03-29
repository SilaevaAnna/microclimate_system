# Уникальные идентификаторы для каждого датчика (генерируются один раз)
import uuid

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
