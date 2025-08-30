from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import jwt_required, get_jwt_identity

from .service import PlaygroundsService

def create_playgrounds_router(db: Database) -> Blueprint:
    bp = Blueprint("playgrounds", __name__)
    service = PlaygroundsService(db)

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
    
    return bp
