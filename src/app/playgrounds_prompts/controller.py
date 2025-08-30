from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.helpers.utils import json_error
from .service import PlaygroundsPromptsService


def create_playgrounds_prompts_router(db: Database) -> Blueprint:
    bp = Blueprint("playgrounds_prompts", __name__)
    service = PlaygroundsPromptsService(db)

    @bp.get("/<playground_id>")
    @jwt_required()
    def find_prompts(playground_id: str):
        prompts = service.find_prompts_by_playground_id(playground_id)
        if not prompts:
            return json_error("Not found", 404)
        return jsonify(prompts), 200

    @bp.post("/<playground_id>")
    @jwt_required()
    def create_prompt(playground_id: str):
        data = request.get_json(silent=True) or {}
        data["created_by"] = get_jwt_identity()
        try:
            prompt = service.create_prompt(playground_id, data)
        except ValueError as e:
            return json_error(str(e))
        return jsonify(prompt), 201

    @bp.delete("/<playground_id>/<prompt_id>")
    @jwt_required()
    def delete_prompt(playground_id: str, prompt_id: str):
        service.delete_prompt(prompt_id)
        return jsonify({"message": "Prompt deleted"}), 204

    @bp.put("/<playground_id>/<prompt_id>/like")
    @jwt_required()
    def like_prompt(playground_id: str, prompt_id: str):
        try:
            service.like_prompt(prompt_id)
        except ValueError as e:
            return json_error(str(e))
        return jsonify({"message": "Prompt liked"}), 200

    @bp.put("/<playground_id>/<prompt_id>/dislike")
    @jwt_required()
    def dislike_prompt(playground_id: str, prompt_id: str):
        try:
            service.dislike_prompt(prompt_id)
        except ValueError as e:
            return json_error(str(e))
        return jsonify({"message": "Prompt disliked"}), 200

    return bp
