#!/usr/bin/env python3
"""
Flask web application with intentional issues for testing.
"""

from flask import Flask, request, jsonify
import os
import subprocess
import sqlite3
import secrets

app = Flask(__name__)

# Security issue: hardcoded secret key
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Security issue: debug mode in production-like code
app.config['DEBUG'] = True

# Database connection
def get_db():
    """Database connection with issues."""
    conn = sqlite3.connect('app.db')
    # Issue: no connection closing, potential resource leak
    return conn

@app.route('/')
def index():
    """Home page with some issues."""
    # Issue: unused variable
    unused_var = "not used"

    # Issue: direct string formatting with user input (potential XSS)
    name = request.args.get('name', 'World')
    return f'<h1>Hello {name}!</h1>'

@app.route('/api/users')
def get_users():
    """API endpoint with SQL injection vulnerability."""
    user_id = request.args.get('id')

    # Security issue: SQL injection
    conn = get_db()
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection!
    cursor.execute(query)
    results = cursor.fetchall()

    return jsonify(results)

@app.route('/api/execute')
def execute_command():
    """Dangerous command execution endpoint."""
    cmd = request.args.get('cmd')

    # Security issue: command injection
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return jsonify({'output': result.stdout, 'error': result.stderr})

@app.route('/api/auth')
def authenticate():
    """Authentication with weak password validation."""
    password = request.args.get('password')

    # Issue: weak password check
    if password == "admin123":  # hardcoded password
        return jsonify({'authenticated': True})
    return jsonify({'authenticated': False})

@app.route('/api/random')
def get_random():
    """Random number generation - should use secrets instead."""
    import random

    # Issue: using random instead of secrets for security
    token = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(32))
    return jsonify({'token': token})

def process_data(data):
    """Data processing function with code quality issues."""
    # Issue: too many blank lines and poor formatting
    if data is None:
        return None


    # Issue: inconsistent indentation and spacing
    result = []
    for item in data:
        if item:
            result.append(item.upper())
    return result

# Issue: unused function
def unused_function():
    """This function is never called."""
    return "unused"

# Issue: poor exception handling
@app.route('/api/divide')
def divide_numbers():
    """Division endpoint with poor error handling."""
    a = int(request.args.get('a', 0))
    b = int(request.args.get('b', 1))

    # Issue: no try/catch for division by zero
    result = a / b
    return jsonify({'result': result})

if __name__ == '__main__':
    # Issue: running with debug=True in production-like code
    app.run(host='0.0.0.0', port=5000, debug=True)
