#auth.py
from flask import Blueprint, current_app, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from bson.objectid import ObjectId
from validators import RegisterModel, LoginModel, UpdateModel
from pydantic import ValidationError
from utils.helpers import to_jsonable
from flask_cors import cross_origin

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    db = current_app.db
    try:
        payload = RegisterModel(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422

    if db.users.find_one({"email": payload.email}):
        return jsonify({"error": "Email already registered"}), 400

    pwd_hash = generate_password_hash(payload.password)
    now = __import__("datetime").datetime.utcnow()

    user = {
        "name": payload.name,
        "email": payload.email,
        "role": payload.role,
        "password_hash": pwd_hash,
        "created_at": now,
        "updated_at": now
    }

    res = db.users.insert_one(user)
    new_user = db.users.find_one({"_id": res.inserted_id})

    return jsonify({"msg": "Registered", "user": to_jsonable(new_user, exclude=["password_hash"])}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    db = current_app.db
    try:
        payload = LoginModel(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422

    user = db.users.find_one({"email": payload.email})
    if not user or not check_password_hash(user["password_hash"], payload.password):
        return jsonify({"error": "Invalid credentials"}), 401

    identity = str(user["_id"])
    claims = {"email": user["email"], "name": user["name"]}

    access = create_access_token(identity=identity, additional_claims=claims)
    refresh = create_refresh_token(identity=identity)

    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "user": to_jsonable(user, exclude=["password_hash"])
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    db = current_app.db
    jti = get_jwt()["jti"]
    now = __import__("datetime").datetime.utcnow()
    db.token_blocklist.insert_one({"jti": jti, "type": "access", "created_at": now})
    return jsonify({"msg": "Logged out"}), 200


@auth_bp.route("/logout_refresh", methods=["POST"])
@jwt_required(refresh=True)
def logout_refresh():
    db = current_app.db
    jti = get_jwt()["jti"]
    now = __import__("datetime").datetime.utcnow()
    db.token_blocklist.insert_one({"jti": jti, "type": "refresh", "created_at": now})
    return jsonify({"msg": "Refresh token revoked"}), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    db = current_app.db
    identity = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(identity)})

    if not user:
        return jsonify({"error": "User not found"}), 404

    claims = {"email": user["email"], "name": user["name"]}
    access = create_access_token(identity=identity, additional_claims=claims)

    return jsonify({"access_token": access}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    db = current_app.db
    identity = get_jwt_identity()
    user = db.users.find_one({"_id": ObjectId(identity)})

    return jsonify(to_jsonable(user, exclude=["password_hash"])), 200


@auth_bp.route("/update", methods=["PUT", "PATCH"])
@jwt_required()
def update_user():
    db = current_app.db
    identity = get_jwt_identity()

    try:
        uid = ObjectId(identity)
    except:
        return jsonify({"error": "Invalid user id"}), 400

    try:
        payload = UpdateModel(**(request.get_json() or {}))
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422

    updates = {}
    if payload.name:
        updates["name"] = payload.name
    if payload.email:
        if db.users.find_one({"email": payload.email, "_id": {"$ne": uid}}):
            return jsonify({"error": "Email already in use"}), 400
        updates["email"] = payload.email
    if payload.password:
        updates["password_hash"] = generate_password_hash(payload.password)

    updates["updated_at"] = __import__("datetime").datetime.utcnow()

    db.users.update_one({"_id": uid}, {"$set": updates})
    user = db.users.find_one({"_id": uid})

    return jsonify({"msg": "Updated", "user": to_jsonable(user, exclude=["password_hash"])}), 200



