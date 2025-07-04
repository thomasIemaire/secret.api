from src.app.agents.agents_model import AgentModel

class FlowsStepModel:
    name: str
    agent: AgentModel

class FlowModel:
    name: str
    sardine: AgentModel
    supported_documents: list[str]
    steps: list[FlowsStepModel]