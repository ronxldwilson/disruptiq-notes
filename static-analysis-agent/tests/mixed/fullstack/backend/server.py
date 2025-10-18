#!/usr/bin/env python3
"""
Backend server for fullstack app with issues.
"""

from flask import Flask, request, jsonify
import sqlite3
import subprocess
import os

app = Flask(__name__)

# Issue: hardcoded configuration
app.config.update(
    SECRET_KEY='dev-secret-key',
    DATABASE='app.db',
    DEBUG=True
)

def get_db_connection():
    """Database connection with issues."""
    # Issue: no connection pooling
    conn = sqlite3.connect(app.config['DATABASE'])
    return conn

@app.route('/api/users')
def get_users():
    """Get users with SQL injection."""
    user_id = request.args.get('id')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Security issue: SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    results = cursor.fetchall()

    return jsonify(results)

@app.route('/api/execute', methods=['POST'])
def execute_code():
    """Execute code with command injection."""
    code = request.json.get('code')

    # Security issue: command injection
    result = subprocess.run(['python3', '-c', code],
                          capture_output=True, text=True)

    return jsonify({
        'output': result.stdout,
        'error': result.stderr
    })

@app.route('/api/files/<path:filename>')
def get_file(filename):
    """File access with path traversal."""
    # Issue: no path validation
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

# Issue: unused function
def helper_function():
    """Never used helper."""
    return "helper"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
