from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import jwt_required, get_jwt_identity
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
            return jsonify({"error": str(e)}), 400
        
        return jsonify(created), 201

    @bp.post("/login")
    def login():
        data = request.get_json() or {}

        try:
            user = service.login(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        return jsonify(user), 200
    
    @bp.post("/token")
    @jwt_required()
    def token():
        current_user = get_jwt_identity()
        
        try:
            user = service.login_token(current_user)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        return jsonify(user), 200
    
    @bp.get("/email-exists")
    def email_exists():
        email = request.args.get("email")
        if not email:
            return jsonify({"error": "Email parameter is required"}), 400
        
        exists = service.email_exists(email)
        return jsonify({"exists": exists}), 200

    return bp