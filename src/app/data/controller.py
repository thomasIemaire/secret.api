from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.app.models import service
from .service import DataService

def create_data_router(db: Database) -> Blueprint:
    bp = Blueprint("data", __name__)
    service = DataService(db)

    @bp.get("/")
    @jwt_required()
    def find_data():
        docs = service.find()
        if not docs:
            return jsonify({"error": "Not found"}), 404
        return jsonify(docs), 200

    @bp.post("/")
    @jwt_required()
    def create_data():
        user_id = get_jwt_identity()
        data = request.json
        if not data:
            return jsonify({"error": "Bad request"}), 400
        data = service.create(user_id, data)
        return jsonify(data), 201

    @bp.get("/<id>")
    @jwt_required()
    def get_data(id):
        doc = service.find_one_by_id(id)
        if not doc:
            return jsonify({"error": "Not found"}), 404
        return jsonify(doc), 200

    return bp
