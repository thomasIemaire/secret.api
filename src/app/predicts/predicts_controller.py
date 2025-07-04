from flask import Blueprint, jsonify, request

from src.app.predicts.predicts_service import PredictsService

def create_predicts_router(db):
    predicts_router = Blueprint('predicts', __name__)
    predicts_service = PredictsService()

    @predicts_router.route('/', methods=['POST'])
    def predict_document():
        request_data = request.get_json()

        if not request_data or 'base64' not in request_data:
            return jsonify({'error': 'Invalid input, document is required'}), 400
        
        try:
            base64 = request_data['base64']
            flow = request_data.get('flow', None)

            prediction = predicts_service.predict_document(base64, flow)
            if not prediction:
                return jsonify({'error': 'Prediction failed'}), 500
            return jsonify(prediction.to_dict()), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return predicts_router