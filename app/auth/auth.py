from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from ..database.db_connection import execute_query
from .validators import validate_registration_data, validate_login_data, ValidationError


def register_user(username, password, email):
    try:
        # Validate input
        validated_data = validate_registration_data({
            'username': username,
            'password': password,
            'email': email
        })
        
        # Check if user exists
        existing_user = execute_query(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (validated_data['username'], validated_data['email']),
            fetch_one=True
        )
        
        if existing_user:
            return {"success": False, "message": "User already exists"}
        
        # Create user
        hashed_password = generate_password_hash(validated_data['password'])
        execute_query(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (validated_data['username'], hashed_password, validated_data['email'])
        )
        
        return {"success": True, "message": "User registered successfully"}
    
    except ValidationError as e:
        return {"success": False, "message": "Validation failed", "errors": str(e)}
    except Exception as e:
        return {"success": False, "message": "Registration failed"}


def login_user(username, password):
    try:
        # Validate input
        validated_data = validate_login_data({
            'username': username,
            'password': password
        })
        
        # Get user
        user = execute_query(
            "SELECT id, password FROM users WHERE username = ?",
            (validated_data['username'],),
            fetch_one=True
        )
        
        if user and check_password_hash(user['password'], validated_data['password']):
            access_token = create_access_token(identity=user['id'])
            return {"success": True, "token": access_token, "user_id": user['id']}
        else:
            return {"success": False, "message": "Invalid credentials"}
    
    except ValidationError as e:
        return {"success": False, "message": "Validation failed", "errors": str(e)}
    except Exception as e:
        return {"success": False, "message": "Login failed"}