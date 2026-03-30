# actuator_service.py
import sqlite3


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
        actions.append(('heater', 'turn_on', f'Температура низкая: {temp}C'))
    elif temp > 26:
        actions.append(('fan', 'turn_on', f'Температура высокая: {temp}C'))
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

    # Проверка CO2
    if co2 > 1000:
        actions.append(('fan', 'turn_on', f'CO2 критический: {co2} ppm'))

    # Применение действий
    for device_name, action, reason in actions:
        if action == 'turn_on':
            cursor.execute(
                "UPDATE actuators SET state = 'on', updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (device_name,)
            )
            if reason:
                print(f"  {device_name.upper()}: ВКЛЮЧЕН ({reason})")
        elif action == 'turn_off':
            cursor.execute(
                "UPDATE actuators SET state = 'off', updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                (device_name,)
            )

    conn.commit()
    conn.close()

    return actions
