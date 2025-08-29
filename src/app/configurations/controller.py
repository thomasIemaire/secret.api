from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.app.models import service
from .service import ConfigurationsService

def create_configurations_router(db: Database) -> Blueprint:
    bp = Blueprint("configurations", __name__)
    service = ConfigurationsService(db)

    @bp.get("/")
    @jwt_required()
    def find_configurations():
        docs = service.find_all()
        if not docs:
            return jsonify({"error": "Not found"}), 404
        return jsonify(docs), 200

    @bp.post("/")
    @jwt_required()
    def create_configuration():
        user_id = get_jwt_identity()
        data = request.json
        if not data:
            return jsonify({"error": "Bad request"}), 400
        configuration = service.create(user_id, data)
        return jsonify(configuration), 201
    
    @bp.get("/<id>")
    @jwt_required()
    def get_configuration(id):
        doc = service.find_one_by_id(id)
        if not doc:
            return jsonify({"error": "Not found"}), 404
        return jsonify(doc), 200

    return bp
