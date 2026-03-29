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
            if self.buffer.full():
                self.buffer.get()
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


from threading import Thread
from app.services.sensor_generator import generate_test_data


class DataAcquisitionService:
    def __init__(self, buffer, data_generator, control_service, notification_service, interval=5):
        self.buffer = buffer
        self.data_generator = data_generator
        self.control_service = control_service
        self.notification_service = notification_service
        self.interval = interval
        self.running = False

    def start(self):
        self.running = True
        Thread(target=self._run, daemon=True).start()

    def _run(self):
        while self.running:
            try:
                data = self.data_generator()

                self.buffer.add_data({
                    "timestamp": datetime.now().isoformat(),
                    "data": data
                })

                self.control_service.process(data)
                self.notification_service.process(data)

                time.sleep(self.interval)

            except Exception as e:
                print(f"Ошибка в DataAcquisitionService: {e}")


from app.database.database import insert_sensor_readings_batch


class DataPersistenceService:
    def __init__(self, buffer, flush_interval=10):
        self.buffer = buffer
        self.flush_interval = flush_interval
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = Thread(target=self._flush_loop, daemon=True)
        self.thread.start()

    def _flush_loop(self):
        while self.running:
            try:
                batch = self.buffer.get_data_batch(20)

                if batch:
                    insert_sensor_readings_batch(batch)
                    print(f"✓ Записано в БД: {len(batch)} записей")

                time.sleep(self.flush_interval)

            except Exception as e:
                print(f"Ошибка записи в БД: {e}")