from src.app.flows.flows_model import FlowModel
from src.helpers.flow import FlowManager
from src.helpers.sardine import Sardine
from src.app.predicts.predicts_model import PredictModel

class PredictsService:

    def __init__(self):
        pass

    def predict_document(self, base64: str, flow: FlowModel = None) -> PredictModel:
        sardine = Sardine(flow["sardine"]["name"], flow["sardine"]["version"])
        sardine.load_document(base64)
        
        flow_manager = FlowManager(sardine, flow["supported_documents"], flow["steps"])
        flow_manager.run_flow()

        return PredictModel(
            name="Document Prediction",
            type="document",
            data=sardine._document.to_dict(),
            flow=flow_manager.to_dict()
        )