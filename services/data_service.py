from threading import Lock
from queue import Queue
import datetime
import time


class DataBuffer:
    def __init__(self, max_size=100):
        self.buffer = Queue(maxsize=max_size)
        self.lock = Lock()
        self.running = True

    def add_data(self, data):
        """Добавление данных в буфер"""
        with self.lock:
            self.buffer.put(data)

    def get_data_batch(self, batch_size=10):
        """Получение пакета данных из буфера"""
        with self.lock:
            batch = []
            for _ in range(min(batch_size, self.buffer.qsize())):
                batch.append(self.buffer.get())
            return batch

    def is_empty(self):
        """Проверка, пуст ли буфер"""
        with self.lock:
            return self.buffer.empty()


# data_service.py
from threading import Thread
from domain.sensors import generate_test_data


class DataAcquisitionService:
    def __init__(self, buffer, update_interval=5):
        self.buffer = buffer
        self.update_interval = update_interval
        self.running = False
        self.thread = None

    def start(self):
        """Запуск сервиса сбора данных"""
        self.running = True
        self.thread = Thread(target=self._acquire_data, daemon=True)
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

                # Ожидание до следующего цикла
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Ошибка в сервисе сбора данных: {e}")

    def _check_critical_values(self, data):
        """Проверка критических значений и немедленная реакция"""
        # Реализация проверки критических значений
        # и немедленной реакции (без ожидания записи в БД)
        if data['co2'] > 1500:
            # Немедленная реакция на критическое значение
            print("КРИТИЧЕСКОЕ ЗНАЧЕНИЕ СО2! Срочное проветривание!")
            # Здесь можно вызвать уведомления или другие действия