from pymongo.database import Database
from bson.objectid import ObjectId
from src.helpers.base_service import BaseService

class ConfigurationsService(BaseService):
    collection_name = "configurations"

    def find_all(self) -> list[dict]:
        return self.find(sort=[("created_at", -1)], projection={"attributes": 0, "formats": 0, "randomizers": 0})

    def find_one_by_id(self, id: str) -> dict | None:
        return self.find_one({"_id": ObjectId(id)})

    def create(self, user_id: str, data: dict) -> dict:
        doc = {
            "name": data.get("name"),
            "description": data.get("description"),
            "attributes": data.get("attributes", []),
            "formats": data.get("formats", []),
            "randomizers": data.get("randomizers", []),
            "created_by": ObjectId(user_id),
            "created_at": self.get_current_time(),
        }

        self.insert_one(doc)

        return self.serialize(doc)