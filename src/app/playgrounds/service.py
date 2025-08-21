from typing import Any, Dict, List, Optional
from pymongo.database import Database
from bson.objectid import ObjectId
from src.helpers.base_service import BaseService

class PlaygroundsService(BaseService):
    collection_name = "playgrounds"

    def find_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.find({
            "$or": [
                {"created_by": ObjectId(user_id)},
                {"shared_with": ObjectId(user_id)}
            ]
        })

    def create_playground(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get("name"):
            raise ValueError("Playground name is required")
        playground = {
            "created_by": ObjectId(user_id),
            "name": data["name"],
            "shared_with": data.get("shared_with", []),
            "created_at": self.get_current_time(),
        }
        return self.insert_one(playground)
        
class PlaygroundsPromptsService(BaseService):
    collection_name = "playground_prompts"

    def find_prompts_by_playground_id(self, playground_id: str) -> List[Dict[str, Any]]:
        return self.find({"playground_id": ObjectId(playground_id)})

    def create_prompt(self, playground_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        playground = PlaygroundsService(db=self.db).find_one({"_id": ObjectId(playground_id)})
        if not playground:
            raise ValueError("Playground not found")

        if not data.get("content") or not data.get("system"):
            raise ValueError("Prompt content and system are required")
        prompt = {
            "playground_id": ObjectId(playground_id),
            "content": data["content"],
            "system": data.get("system", None),
            "created_at": self.get_current_time(),
            "created_by": ObjectId(data.get("created_by")),
        }
        return self.insert_one(prompt)