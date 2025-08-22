from pymongo.database import Database
from bson.objectid import ObjectId
from src.helpers.base_service import BaseService

class ModelsService(BaseService):
    collection_name = "models"

    def find_all(self) -> list[dict]:
        return self.find(sort=[("updated_at", -1)], projection={"mapper": 0, "parameters": 0})

    def create(self, user_id: str, model_data: dict) -> ObjectId:
        """Créer un nouveau modèle pour un utilisateur donné."""
        doc = {
            "name": model_data.get("name", "Untitled Model"),
            "description": model_data.get("description", ""),
            "reference": model_data.get("reference", ""),
            "version": model_data.get("version", "1.0"),
            "mapper": model_data.get("mapper", {}),
            "parameters": model_data.get("parameters", {}),
            "created_by": ObjectId(user_id),
            "updated_by": ObjectId(user_id),
            "created_at": self.get_current_time(),
            "updated_at": self.get_current_time(),
        }

        self.col.insert_one(doc)

        return self.serialize(doc)