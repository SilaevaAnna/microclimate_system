# check_data.py
import sqlite3

conn = sqlite3.connect('climate_system.db')
cursor = conn.cursor()

# Проверка количества записей
cursor.execute('SELECT COUNT(*) FROM sensor_readings')
count = cursor.fetchone()[0]
print(f"Количество записей в базе: {count}")

# Проверка последних 5 записей
if count > 0:
    print("\nПоследние 5 записей:")
    cursor.execute('SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 5')
    for row in cursor.fetchall():
        print(f"ID: {row[0]}, Время: {row[1]}, Темп: {row[2]}, Влажн: {row[3]}, CO2: {row[4]}")
else:
    print("\n⚠️ База данных пуста! Нужно сгенерировать данные.")

conn.close()