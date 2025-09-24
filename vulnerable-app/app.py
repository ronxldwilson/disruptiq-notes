
# app.py
from flask import Flask, request, jsonify, g
import sqlite3

DB = "/data/demo.db"
app = Flask(__name__)

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
    return "SQLi demo app"

# Vulnerable GET endpoint: user id in query string used unsafely
@app.route("/user")
def get_user():
    user_id = request.args.get("id", "")
    # Intentional insecure string concatenation (vulnerable)
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

# Vulnerable POST endpoint: form-encoded
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

# Vulnerable JSON endpoint
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
