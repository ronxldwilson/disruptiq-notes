#!/usr/bin/env python3
"""
Python file with intentional security vulnerabilities.
"""

import os
import subprocess
import pickle
import yaml
import random
import hashlib
import sqlite3

# Security issue: hardcoded credentials
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "admin123"
JWT_SECRET = "my-secret-key"

def weak_password_hash(password):
    """Weak password hashing."""
    # Issue: using MD5 for passwords
    return hashlib.md5(password.encode()).hexdigest()

def insecure_random():
    """Using random instead of secrets."""
    # Issue: cryptographically weak random
    return random.random()

def sql_injection_vulnerable(user_input):
    """SQL injection vulnerability."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Issue: direct string formatting in SQL
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    cursor.execute(query)

    return cursor.fetchall()

def command_injection(cmd_input):
    """Command injection vulnerability."""
    # Issue: shell=True with user input
    result = subprocess.run(cmd_input, shell=True, capture_output=True)
    return result.stdout.decode()

def pickle_deserialization(data):
    """Unsafe pickle deserialization."""
    # Security issue: loading untrusted pickle data
    return pickle.loads(data)

def yaml_load_unsafe(yaml_data):
    """Unsafe YAML loading."""
    # Issue: using unsafe YAML loader
    return yaml.load(yaml_data, Loader=yaml.FullLoader)  # Still not safe with untrusted data

def path_traversal(filepath):
    """Path traversal vulnerability."""
    # Issue: no path validation
    with open(filepath, 'r') as f:
        return f.read()

def weak_session_id():
    """Weak session ID generation."""
    # Issue: predictable session IDs
    return str(random.randint(1000, 9999))

def eval_execution(user_code):
    """Dangerous eval execution."""
    # Security issue: executing user-provided code
    return eval(user_code)

def unsafe_deserialization(json_data):
    """Unsafe deserialization simulation."""
    import json

    # Issue: trusting user input for object creation
    data = json.loads(json_data)
    if data.get('type') == 'user':
        # Simulating unsafe object creation
        return f"Created user: {data.get('name')}"
    return None

def main():
    """Main function demonstrating vulnerabilities."""
    # These would be flagged by security tools
    weak_hash = weak_password_hash("password123")
    insecure_rand = insecure_random()
    sql_result = sql_injection_vulnerable("admin' OR '1'='1")
    cmd_result = command_injection("echo 'hello world'")
    session_id = weak_session_id()

    print(f"Hash: {weak_hash}")
    print(f"Random: {insecure_rand}")
    print(f"SQL result: {sql_result}")
    print(f"Command result: {cmd_result}")
    print(f"Session ID: {session_id}")

if __name__ == '__main__':
    main()
