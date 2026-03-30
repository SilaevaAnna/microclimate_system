# database.py
import sqlite3
from werkzeug.security import generate_password_hash


def init_db():
    conn = sqlite3.connect('../../climate_system.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица показаний датчиков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL,
            co2 INTEGER,
            voc INTEGER,
            pm2_5 INTEGER,
            pm10 INTEGER
        )
    ''')

    # Таблица состояний актуаторов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actuators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            state TEXT DEFAULT 'off',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица уведомлений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Инициализация актуаторов
    cursor.execute("INSERT OR IGNORE INTO actuators (name, type, state) VALUES ('humidifier', 'relay', 'off')")
    cursor.execute("INSERT OR IGNORE INTO actuators (name, type, state) VALUES ('fan', 'relay', 'off')")
    cursor.execute("INSERT OR IGNORE INTO actuators (name, type, state) VALUES ('heater', 'relay', 'off')")

    # Создание тестового пользователя с правильным хэшем пароля
    # Пароль: password123
    test_password_hash = generate_password_hash('password123')
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, password, email) VALUES (?, ?, ?)",
        ('testuser', test_password_hash, 'test@example.com')
    )

    conn.commit()
    conn.close()
    print("Database initialized")
    print("Test user created: testuser / password123")


def insert_sensor_readings_batch(batch):
    conn = sqlite3.connect('../../climate_system.db')
    cursor = conn.cursor()

    cursor.executemany('''
        INSERT INTO sensor_readings (
            timestamp, temperature, humidity, co2, voc, pm2_5, pm10
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [
        (
            item['timestamp'],
            item['data']['temperature'],
            item['data']['humidity'],
            item['data']['co2'],
            item['data']['voc'],
            item['data']['pm2_5'],
            item['data']['pm10']
        )
        for item in batch
    ])

    conn.commit()
    conn.close()