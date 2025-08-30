from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.helpers.utils import json_error
from .service import AuthService

def create_auth_router(db: Database) -> Blueprint:
    bp = Blueprint("auth", __name__)
    service = AuthService(db)

    @bp.post("/register")
    def register():
        data = request.get_json() or {}

        try:
            created = service.register(data)
        except ValueError as e:
            return json_error(str(e))
        
        return jsonify(created), 201

    @bp.post("/login")
    def login():
        data = request.get_json() or {}

        try:
            user = service.login(data)
        except ValueError as e:
            return json_error(str(e))

        return jsonify(user), 200
    
    @bp.post("/token")
    @jwt_required()
    def token():
        current_user = get_jwt_identity()
        
        try:
            user = service.login_token(current_user)
        except ValueError as e:
            return json_error(str(e))

        return jsonify(user), 200
    
    @bp.get("/email-exists")
    def email_exists():
        email = request.args.get("email")
        if not email:
            return json_error("Email parameter is required")
        
        exists = service.email_exists(email)
        return jsonify({"exists": exists}), 200

    return bp
