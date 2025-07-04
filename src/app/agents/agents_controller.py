from flask import Blueprint, jsonify, request

from src.app.agents.agents_service import AgentsService

def create_agents_router(db):
    agents_router = Blueprint('agents', __name__)
    agents_service = AgentsService(db)

    @agents_router.route('/', methods=['GET'])
    def get_agents():
        agents = agents_service.get_agents()
        if not agents:
            return jsonify({'message': 'No agents found'}), 404
        return jsonify(agents), 200


    return agents_router