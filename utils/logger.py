# utils/logger.py
import logging
from datetime import datetime
import os
import threading
import time
from app import generate_test_data

def setup_logger():
    """Настройка логгера"""
    logger = logging.getLogger('iot_system')
    logger.setLevel(logging.INFO)

    # Создаем директорию для логов, если её нет
    os.makedirs('logs', exist_ok=True)

    # Формат логов
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Логирование в файл
    log_filename = f'logs/iot_system_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Логирование в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Создаем глобальный логгер
logger = setup_logger()


class DataAcquisitionService:
    def __init__(self, buffer, update_interval=5):
        self.buffer = buffer
        self.update_interval = update_interval
        self.running = False
        self.thread = None
        self.logger = logging.getLogger('iot_system.data_acquisition')

    def start(self):
        """Запуск сервиса сбора данных"""
        self.logger.info("Запуск сервиса сбора данных")
        self.running = True
        self.thread = threading.Thread(target=self._acquire_data, daemon=True)
        self.thread.start()

    def _acquire_data(self):
        """Цикл сбора данных с датчиков"""
        while self.running:
            try:
                # Генерация данных с датчиков
                data = generate_test_data()

                # Добавление данных в буфер
                self.buffer.add_data({
                    'timestamp': datetime.now().isoformat(),
                    'data': data
                })

                # Проверка критических значений
                self._check_critical_values(data)

                # Логирование собранных данных
                self.logger.info(f"Собраны данные: {data}")  # Исправлено: переменная data теперь определена

                # Ожидание до следующего цикла
                time.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"Ошибка в сервисе сбора данных: {e}")

    def _check_critical_values(self, data):
        """Проверка критических значений и немедленная реакция"""
        # Реализация проверки критических значений
        if data['co2'] > 1500:
            self.logger.warning(f"КРИТИЧЕСКОЕ ЗНАЧЕНИЕ СО2! Текущее значение: {data['co2']} ppm")
            # Немедленная реакция на критическое значение
            print("КРИТИЧЕСКОЕ ЗНАЧЕНИЕ СО2! Срочное проветривание!")