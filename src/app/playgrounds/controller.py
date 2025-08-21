from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .service import PlaygroundsService, PlaygroundsPromptsService

def create_playgrounds_router(db: Database) -> Blueprint:
    bp = Blueprint("playgrounds", __name__)
    service = PlaygroundsService(db)
    prompts_service = PlaygroundsPromptsService(db)

    @bp.get("/")
    @jwt_required()
    def find_playgrounds_by_user_id():
        user_id = get_jwt_identity()
        doc = service.find_by_user_id(user_id)
        if not doc:
            return jsonify({"error": "Not found"}), 404
        return jsonify(doc), 200

    @bp.post("/")
    @jwt_required()
    def create_playground():
        data = request.get_json() or {}
        user_id = get_jwt_identity()
        try:
            playground = service.create_playground(user_id, data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        return jsonify(playground), 201
    
    @bp.get("/<playground_id>")
    @jwt_required()
    def find_playground_by_id(playground_id: str):
        doc = prompts_service.find_prompts_by_playground_id(playground_id)
        if not doc:
            return jsonify({"error": "Not found"}), 404
        return jsonify(doc), 200

    @bp.post("/<playground_id>")
    @jwt_required()
    def create_prompt(playground_id: str):
        data = request.get_json() or {}
        user_id = get_jwt_identity()
        data["created_by"] = user_id
        try:
            prompt = prompts_service.create_prompt(playground_id, data)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        return jsonify(prompt), 201

    return bp
