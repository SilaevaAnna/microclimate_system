# interfaces.py
from abc import ABC, abstractmethod


class IDataService(ABC):
    @abstractmethod
    def start(self):
        """Запуск сервиса сбора данных"""
        pass

    @abstractmethod
    def stop(self):
        """Остановка сервиса сбора данных"""
        pass

    @abstractmethod
    def get_current_data(self):
        """Получение текущих данных"""
        pass


class IStorageService(ABC):
    @abstractmethod
    def save_data(self, data):
        """Сохранение данных в хранилище"""
        pass

    @abstractmethod
    def get_data(self, start_time, end_time):
        """Получение данных за период"""
        pass