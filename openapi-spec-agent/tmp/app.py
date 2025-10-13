from flask import Flask

app = Flask(__name__)

@app.route("/users", methods=["GET"])
def get_users():
    return "List of users"

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    return f"User {user_id}"

@app.route("/users", methods=["POST"])
def create_user():
    return "User created"
