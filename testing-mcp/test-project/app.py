import os
import sqlite3

# Hardcoded password - should be flagged
password = "supersecretpassword123"

def login(user, passwd):
    if passwd == password:
        return True
    return False

def execute_query(query):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    # SQL injection vulnerability
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def dangerous_code(user_input):
    # Using eval - dangerous
    result = eval(user_input)
    return result

if __name__ == "__main__":
    print("Testing app")
    print(login("user", "supersecretpassword123"))
    print(execute_query("SELECT * FROM users"))
    print(dangerous_code("1 + 1"))
