from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .service import ModelsService

def create_models_router(db: Database) -> Blueprint:
    bp = Blueprint("models", __name__)
    service = ModelsService(db)

    @bp.get("/")
    @jwt_required()
    def find_models():
        docs = service.find_all()
        if not docs:
            return jsonify({"error": "Not found"}), 404
        return jsonify(docs), 200
    
    @bp.post("/")
    @jwt_required()
    def create_model():
        user_id = get_jwt_identity()
        data = request.json
        if not data:
            return jsonify({"error": "Bad request"}), 400
        model = service.create(user_id, data)
        return jsonify(model), 201
    
    @bp.post("/build/<model_id>")
    @jwt_required()
    def build_model(model_id):
        try:
            parameters = request.json or {}
            model = service.build_model(model_id, parameters)
            return jsonify(model), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    return bp
