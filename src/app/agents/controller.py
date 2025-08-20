from flask import Blueprint, jsonify, request
from pymongo.database import Database
from .service import AgentsService

def create_agents_router(db: Database) -> Blueprint:
    bp = Blueprint("agents", __name__)
    service = AgentsService(db)

    @bp.get("/")
    def find_agents():
        return jsonify(service.find()), 200

    @bp.post("/")
    def create_agent():
        data = request.get_json() or {}
        created = service.insert_one(data)
        return jsonify(created), 201

    @bp.get("/<agent_id>")
    def find_agent_by_id(agent_id: str):
        doc = service.find_one(agent_id)
        if not doc:
            return jsonify({"error": "Not found"}), 404
        return jsonify(doc), 200

    return bp
