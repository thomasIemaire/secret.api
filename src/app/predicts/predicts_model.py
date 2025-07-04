class PredictModel:
    name: str
    type: str
    data: dict
    flow: dict

    def __init__(self, name: str, type: str, data: dict, flow: dict):
        self.name = name
        self.type = type
        self.data = data
        self.flow = flow

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "data": self.data,
            "flow": self.flow
        }