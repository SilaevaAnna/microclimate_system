# validators.py
import re
from typing import Dict, Any
from flask import request
from werkzeug.security import generate_password_hash


class ValidationError(Exception):
    pass


def validate_registration_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user registration data"""
    errors = {}
    
    # Username validation
    username = data.get('username', '').strip()
    if not username:
        errors['username'] = 'Username is required'
    elif len(username) < 3 or len(username) > 50:
        errors['username'] = 'Username must be between 3 and 50 characters'
    elif not re.match(r'^[a-zA-Z0-9_]+$', username):
        errors['username'] = 'Username can only contain letters, numbers, and underscores'
    
    # Email validation
    email = data.get('email', '').strip()
    if not email:
        errors['email'] = 'Email is required'
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        errors['email'] = 'Invalid email format'
    
    # Password validation
    password = data.get('password', '')
    if not password:
        errors['password'] = 'Password is required'
    elif len(password) < 8:
        errors['password'] = 'Password must be at least 8 characters'
    elif not re.search(r'[A-Z]', password):
        errors['password'] = 'Password must contain at least one uppercase letter'
    elif not re.search(r'[a-z]', password):
        errors['password'] = 'Password must contain at least one lowercase letter'
    elif not re.search(r'\d', password):
        errors['password'] = 'Password must contain at least one digit'
    elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors['password'] = 'Password must contain at least one special character'
    
    if errors:
        raise ValidationError(errors)
    
    return {
        'username': username,
        'email': email,
        'password': password
    }


def validate_login_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user login data"""
    errors = {}
    
    if not data.get('username', '').strip():
        errors['username'] = 'Username is required'
    
    if not data.get('password', ''):
        errors['password'] = 'Password is required'
    
    if errors:
        raise ValidationError(errors)
    
    return {
        'username': data['username'].strip(),
        'password': data['password']
    }


def validate_actuator_control(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate actuator control data"""
    errors = {}
    
    valid_devices = ['humidifier', 'fan', 'heater']
    valid_actions = ['toggle', 'turn_on', 'turn_off']
    
    device = data.get('device', '').strip()
    action = data.get('action', '').strip()
    
    if not device:
        errors['device'] = 'Device name is required'
    elif device not in valid_devices:
        errors['device'] = f'Invalid device. Must be one of: {", ".join(valid_devices)}'
    
    if not action:
        errors['action'] = 'Action is required'
    elif action not in valid_actions:
        errors['action'] = f'Invalid action. Must be one of: {", ".join(valid_actions)}'
    
    if errors:
        raise ValidationError(errors)
    
    return {'device': device, 'action': action}
