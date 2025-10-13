from flask import Flask # type: ignore

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

@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    return f"User {user_id} updated"

@app.route("/login", methods=["POST"])
def login():
    return "User logged in"

if __name__ == "__main__":
    app.run(debug=True)