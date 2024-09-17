from flask import Blueprint
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from authentication.Auth import Auth
from flask import (
    request,
    jsonify,
    abort,
    redirect,
)


auth = Blueprint('auth', __name__)
AUTH = Auth()

@auth.route("/", methods=["GET"], strict_slashes=False)
def index() -> str:
    """Start the auth"""
    return jsonify({"message": "Bienvenue"})


@auth.route("/signup", methods=["POST"], strict_slashes=False)
def users() -> str:
    """
    Register new users
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    try:
        user = AUTH.register_user(email, password)
    except ValueError:
        return jsonify({"message": "email already registered"}), 400

    return jsonify({"email": f"{email}", "message": "user created"})


@auth.route("/login", methods=["POST"], strict_slashes=False)
def login() -> str:
    """
    Log in a user if the credentials provided are correct, and create a new
    session for them.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    print(email, password)
    if not AUTH.valid_login(email, password):
        abort(401)
    session_id = AUTH.create_session(email)
    response = jsonify({"email": email, "message": "logged in"})
    response.set_cookie("session_id", session_id)
    return response


@auth.route("/logout", methods=["DELETE"], strict_slashes=False)
def logout():
    """
    Log out a logged in user and destroy their session
    """
    session_id = request.cookies.get("session_id", None)
    user = AUTH.get_user_from_session_id(session_id)
    if user is None or session_id is None:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect("/")


@auth.route("/profile", methods=["GET"], strict_slashes=False)
def profile() -> str:
    """
    Return a user's email based on session_id in the received cookies
    """
    session_id = request.cookies.get("session_id")
    print(session_id)
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        return jsonify({"email": f"{user.email}"}), 200
    abort(403)


@auth.route("/reset_password", methods=["POST"], strict_slashes=False)
def get_reset_password_token() -> str:
    """
    Generate a token for resetting a user's password
    """
    data = request.get_json()
    email = data.get("email")
    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        abort(403)
    return jsonify({"email": email, "reset_token": reset_token})


@auth.route("/reset_password", methods=["PUT"], strict_slashes=False)
def update_password() -> str:
    """
    Update a user's password
    """
    data = request.get_json()
    email = data.get("email")
    reset_token = data.get("reset_token")
    new_password = data.get("new_password")
    try:
        AUTH.update_password(reset_token, new_password)
    except ValueError:
        abort(403)
    return jsonify({"email": email, "message": "Password updated"})



