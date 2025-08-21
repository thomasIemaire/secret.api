from flask import Blueprint, jsonify, request
from pymongo.database import Database
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from .service import PlaygroundsService

def create_playgrounds_router(db: Database) -> Blueprint:
    bp = Blueprint("playgrounds", __name__)
    service = PlaygroundsService(db)

    @bp.get("/")
    @jwt_required()
    def find_playgrounds_by_user_id():
        user_id = get_jwt_identity()
        doc = service.find_by_user_id(user_id)
        if not doc:
            return jsonify({"error": "Not found"}), 404
        return jsonify(doc), 200
    
    return bp
