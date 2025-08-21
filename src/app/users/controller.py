from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import jwt_required, get_jwt_identity
from .service import UsersService

def create_users_router(db: Database) -> Blueprint:
    bp = Blueprint("users", __name__)
    service = UsersService(db)

    @bp.get("/")
    @jwt_required()
    def find_users():
        return jsonify(service.find()), 200

    @bp.get("/me")
    @jwt_required()
    def find_me():
        current_user = get_jwt_identity()
        doc = service.find_user_by_id(current_user)
        if not doc:
            return jsonify({"error": "Not found"}), 404
        return jsonify(doc), 200
    
    @bp.put("/me/avatar")
    @jwt_required()
    def update_my_avatar():
        current_user = get_jwt_identity()
        service.update_avatar(current_user)
        return jsonify({"message": "Avatar mis à jour"}), 200

    return bp
