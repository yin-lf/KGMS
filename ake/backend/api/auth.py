from flask import Blueprint, request, jsonify, session
from akb.services.user_service import UserService
from core import create_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return create_response(False, message="Missing username or password"), 400

    user_service = UserService()
    if user_service.find_user(username):
        return create_response(False, message="User already exists"), 409

    user = user_service.create_user(username, password)
    if user:
        return create_response(message="User created successfully"), 201
    else:
        return create_response(False, message="Failed to create user"), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return create_response(False, message="Missing username or password"), 400

    user_service = UserService()
    if user_service.verify_user(username, password):
        session["username"] = username
        return create_response(message="Login successful")
    else:
        return (
            create_response(False, message="Invalid username or password"),
            401,
        )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return create_response(message="Logout successful")
