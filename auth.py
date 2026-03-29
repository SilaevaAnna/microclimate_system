from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


def register_user(username, password, email):
    conn = sqlite3.connect('climate_system.db')
    cursor = conn.cursor()

    try:
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hashed_password, email)
        )
        conn.commit()
        return {"success": True, "message": "User registered successfully"}
    except sqlite3.IntegrityError:
        return {"success": False, "message": "User already exists"}
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect('climate_system.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        access_token = create_access_token(identity=user[0])
        return {"success": True, "token": access_token, "user_id": user[0]}
    else:
        return {"success": False, "message": "Invalid credentials"}