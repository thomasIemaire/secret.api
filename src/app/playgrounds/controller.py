from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from .service import PlaygroundsService
from src.app.playgrounds_prompts.service import PlaygroundsPromptsService

def create_playgrounds_router(db: Database) -> Blueprint:
    bp = Blueprint("playgrounds", __name__)
    service = PlaygroundsService(db)
    prompts_service = PlaygroundsPromptsService(db)

    @bp.get("/")
    @jwt_required()
    def find_playgrounds_for_user():
        playgrounds = service.find_by_user_id(get_jwt_identity())
        if not playgrounds:
            return jsonify({"error": "Not found"}), 404
        return jsonify(playgrounds), 200

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
        prompts = prompts_service.find_prompts_by_playground_id(playground_id)
        if not prompts:
            return jsonify({"error": "Not found"}), 404
        return jsonify(prompts), 200

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

    @bp.delete("/<playground_id>/<prompt_id>")
    @jwt_required()
    def delete_prompt(playground_id: str, prompt_id: str):
        prompts_service.delete_prompt(prompt_id)
        return jsonify({"message": "Prompt deleted"}), 204

    @bp.put("/<playground_id>/<prompt_id>/like")
    @jwt_required()
    def like_prompt(playground_id: str, prompt_id: str):
        try:
            prompts_service.like_prompt(prompt_id)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
        return jsonify({"message": "Prompt liked"}), 200

    @bp.put("/<playground_id>/<prompt_id>/dislike")
    @jwt_required()
    def dislike_prompt(playground_id: str, prompt_id: str):
        try:
            prompts_service.dislike_prompt(prompt_id)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        return jsonify({"message": "Prompt disliked"}), 200

    return bp
