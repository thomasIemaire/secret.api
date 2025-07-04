from flask import Blueprint, jsonify, request

from src.app.flows.flows_service import FlowsService

def create_flows_router(db):
    flows_router = Blueprint('flows', __name__)
    flows_service = FlowsService(db)

    @flows_router.route('/', methods=['GET'])
    def get_flows():
        flows = flows_service.get_flows()
        if not flows:
            return jsonify({'message': 'No flows found'}), 404
        return jsonify(flows), 200

    @flows_router.route('/<string:flow_id>', methods=['GET'])
    def get_flow(flow_id):
        flow = flows_service.get_flow(flow_id)
        if not flow:
            return jsonify({'error': 'Flow not found'}), 404
        return jsonify(flow), 200

    @flows_router.route('/', methods=['POST'])
    def create_flow():
        request_data = request.get_json()
        if not request_data or 'name' not in request_data:
            return jsonify({'error': 'Invalid input, name is required'}), 400
        
        new_flow = flows_service.create_flow(request_data['name'], request_data.get('steps', []))

        new_flow["_id"] = str(new_flow["_id"])

        return jsonify({'message': 'Flow created successfully', 'flow': new_flow}), 201
    
    return flows_router