from bson.objectid import ObjectId
from pymongo.database import Database

class FlowsService:

    def __init__(self, db: Database):
        self._collection = db["flows"]

    def get_flows(self):
        flows = self._collection.find()
        return [{**flow, "_id": str(flow["_id"])} for flow in flows]

    def get_flow(self, flow_id):
        try:
            flow = self._collection.find_one({"_id": ObjectId(flow_id)})
        except Exception:
            return None
        if flow:
            flow["_id"] = str(flow["_id"])
        return flow

    def create_flow(self, name, steps):
        new_flow = {
            "name": name,
            "steps": steps
        }
        self._collection.insert_one(new_flow)
        return new_flow
