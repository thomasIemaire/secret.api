from pymongo.database import Database
from bson.objectid import ObjectId
from src.helpers.base_service import BaseService

class DataService(BaseService):
    collection_name = "models_data"

    def find_one_by_id(self, id: str) -> dict | None:
        return self.serialize(self.find_one({"_id": ObjectId(id)}))

    def create(
        self,
        user_id: str,
        data: dict
    ) -> dict:
        doc = {
            "name": data.get("name"),
            "data": data.get("data"),
            "created_at": self.get_current_time(),
            "created_by": ObjectId(user_id),
        }
        
        self.col.insert_one(doc)

        return self.serialize(doc)
