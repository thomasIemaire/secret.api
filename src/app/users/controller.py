from flask import Blueprint, jsonify, request
from pymongo.database import Database
from .service import UsersService

def create_users_router(db: Database) -> Blueprint:
    bp = Blueprint("users", __name__)
    service = UsersService(db)

    @bp.get("/")
    def find_users():
        return jsonify(service.find()), 200

    @bp.post("/register")
    def register():
        data = request.get_json() or {}

        try:
            created = service.register(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        return jsonify(created), 201

    @bp.post("/signin")
    def signin():
        data = request.get_json() or {}

        try:
            user = service.signin(data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        return jsonify(user), 200

    @bp.get("/<user_id>")
    def find_user_by_id(user_id: str):
        doc = service.find_one(user_id)
        if not doc:
            return jsonify({"error": "Not found"}), 404
        return jsonify(doc), 200

    return bp
