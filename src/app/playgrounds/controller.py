from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.helpers.utils import json_error
from .service import PlaygroundsService

def create_playgrounds_router(db: Database) -> Blueprint:
    bp = Blueprint("playgrounds", __name__)
    service = PlaygroundsService(db)

    @bp.get("/")
    @jwt_required()
    def find_playgrounds_for_user():
        playgrounds = service.find_by_user_id(get_jwt_identity())
        if not playgrounds:
            return json_error("Not found", 404)
        return jsonify(playgrounds), 200

    @bp.post("/")
    @jwt_required()
    def create_playground():
        data = request.get_json(silent=True) or {}
        user_id = get_jwt_identity()
        try:
            playground = service.create_playground(user_id, data)
        except ValueError as e:
            return json_error(str(e))
        return jsonify(playground), 201
    
    return bp
