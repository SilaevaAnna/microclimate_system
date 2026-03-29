class CriticalValueHandler:
    def __init__(self, notification_service):
        self.notification_service = notification_service

    def handle_critical_value(self, value_type, value, threshold):
        """Обработка критического значения"""
        message = f"КРИТИЧЕСКОЕ ЗНАЧЕНИЕ: {value_type} = {value} (порог: {threshold})"
        print(f"⚠️ {message}")

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
            from actuator_service import ActuatorService
            actuator_service = ActuatorService()
            actuator_service.control_device("fan", "turn_on")