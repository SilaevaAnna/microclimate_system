import sqlite3


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
            notifications.append(("warning", f"Низкая температура: {temp}C (норма: 18-24C)"))
        elif temp > 26:
            notifications.append(("warning", f"Высокая температура: {temp}C (норма: 18-24C)"))

        # Проверка влажности
        if humidity < 30:
            notifications.append(("warning", f"Низкая влажность: {humidity}% (норма: 30-60%)"))
        elif humidity > 60:
            notifications.append(("warning", f"Высокая влажность: {humidity}% (норма: 30-60%)"))

        # Проверка CO2
        if co2 > 1000:
            notifications.append(("alert", f"КРИТИЧЕСКИЙ уровень CO2: {co2} ppm (норма: 600-800 ppm)"))
        elif co2 > 800:
            notifications.append(("warning", f"Повышенный уровень CO2: {co2} ppm (норма: 600-800 ppm)"))

        # Проверка ЛОС (VOC)
        if voc > 500:
            notifications.append(("alert", f"Высокий уровень ЛОС: {voc} ppb"))
        elif voc > 300:
            notifications.append(("warning", f"Повышенный уровень ЛОС: {voc} ppb"))

        # Проверка пыли PM2.5
        if pm2_5 > 35:
            notifications.append(("alert", f"Высокий уровень пыли PM2.5: {pm2_5} ug/m3 (норма: 0-15 ug/m3)"))
        elif pm2_5 > 15:
            notifications.append(("warning", f"Повышенный уровень пыли PM2.5: {pm2_5} ug/m3"))

        # Проверка пыли PM10
        if pm10 > 50:
            notifications.append(("alert", f"Высокий уровень пыли PM10: {pm10} ug/m3 (норма: 0-25 ug/m3)"))
        elif pm10 > 25:
            notifications.append(("warning", f"Повышенный уровень пыли PM10: {pm10} ug/m3"))

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


class CriticalValueHandler:
    def __init__(self, notification_service):
        self.notification_service = notification_service

    def handle_critical_value(self, value_type, value, threshold):
        """Обработка критического значения"""
        message = f"КРИТИЧЕСКОЕ ЗНАЧЕНИЕ: {value_type} = {value} (порог: {threshold})"
        print(f"WARNING: {message}")

        # Создание уведомления
        self.notification_service.create_notification(
            type="alert",
            message=message,
            critical=True
        )

        # Немедленная реакция
        self._immediate_response(value_type, value)

    def _immediate_response(self, value_type, value):
        """Немедленная реакция на критическое значение"""
        if value_type == "co2" and value > 1500:
            # Включаем вентилятор для немедленного проветривания
            from app.services.actuator_service import ActuatorService
            actuator_service = ActuatorService()
            actuator_service.control_device("fan", "turn_on")
