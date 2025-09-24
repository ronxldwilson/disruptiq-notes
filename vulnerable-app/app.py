# app.py
from flask import Flask, request, jsonify, g, render_template_string
import sqlite3
import os
import pickle
import base64
import requests

DB = "/data/demo.db"
app = Flask(__name__)

# Hardcoded credentials (exposed)
app.config["SECRET_KEY"] = "super-secret-key-that-should-not-be-in-code"
app.config["GITHUB_API_TOKEN"] = "ghp_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"

def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = sqlite3.connect(DB)
        g._db = db
    return db

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_db", None)
    if db:
        db.close()

@app.route("/")
def index():
    return "SQLi, XSS, RCE, LFI, SSRF demo app"

# Vulnerable GET endpoint: user id in query string used unsafely (SQLi)
@app.route("/user")
def get_user():
    user_id = request.args.get("id", "")
    # Intentional insecure string concatenation (vulnerable to SQLi)
    sql = f"SELECT id, username, email FROM users WHERE id = {user_id}"
    try:
        cur = get_db().execute(sql)
        row = cur.fetchone()
        if row:
            return jsonify({"id": row[0], "username": row[1], "email": row[2]})
        return jsonify({"error": "not found"}), 404
    except Exception as e:
        # Return DB error text intentionally (helps detection in test)
        return jsonify({"error": "db error", "msg": str(e)}), 500

# Vulnerable POST endpoint: form-encoded (SQLi)
@app.route("/search", methods=["POST"])
def search_user():
    q = request.form.get("q", "")
    sql = "SELECT id, username FROM users WHERE username LIKE '%" + q + "%'"
    try:
        cur = get_db().execute(sql)
        rows = cur.fetchall()
        return jsonify([{"id": r[0], "username": r[1]} for r in rows])
    except Exception as e:
        return jsonify({"error": "db error", "msg": str(e)}), 500

# Vulnerable JSON endpoint (SQLi)
@app.route("/api/users", methods=["POST"])
def api_users():
    body = request.get_json(silent=True) or {}
    email = body.get("email", "")
    sql = f"SELECT id, username, email FROM users WHERE email = '{email}'"
    try:
        cur = get_db().execute(sql)
        row = cur.fetchone()
        if row:
            return jsonify({"id": row[0], "username": row[1], "email": row[2]})
        return jsonify({"error": "not found"}), 404
    except Exception as e:
        return jsonify({"error": "db error", "msg": str(e)}), 500

# Command Injection vulnerability
@app.route("/tools/dns-lookup")
def dns_lookup():
    host = request.args.get("host", "")
    # Insecure use of os.system (vulnerable to command injection)
    cmd = f"nslookup {host}"
    stream = os.popen(cmd)
    output = stream.read()
    return output, 200, {"Content-Type": "text/plain"}

# XSS vulnerability
@app.route("/hello")
def hello():
    name = request.args.get("name", "guest")
    # Insecurely rendering user input (vulnerable to XSS)
    return render_template_string(f"<h1>Hello, {name}!</h1>")

# Insecure Deserialization vulnerability
@app.route("/pickle", methods=["POST"])
def load_pickle():
    try:
        data = base64.b64decode(request.data)
        # Insecure deserialization of user-provided data
        deserialized_data = pickle.loads(data)
        return jsonify({"status": "ok", "data": str(deserialized_data)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# SSRF vulnerability
@app.route("/proxy")
def proxy():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "url parameter is missing"}), 400
    try:
        # Insecure request to a user-provided URL (vulnerable to SSRF)
        r = requests.get(url)
        return r.text, r.status_code, r.headers.items()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Local File Inclusion (LFI) vulnerability
@app.route("/page")
def page():
    page = request.args.get("p", "index.html")
    try:
        # Insecurely including a file from the filesystem
        with open(os.path.join("/app/pages", page)) as f:
            return f.read()
    except Exception as e:
        return str(e), 404

if __name__ == "__main__":
    # Create a pages directory for the LFI vulnerability
    if not os.path.exists("/app/pages"):
        os.makedirs("/app/pages")
    with open("/app/pages/index.html", "w") as f:
        f.write("<h1>Welcome to the pages section!</h1>")
    app.run(host="0.0.0.0", port=5000)