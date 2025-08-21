from typing import Any, Dict, List, Optional
from pymongo.database import Database
from src.helpers.base_service import BaseService

class PlaygroundsService(BaseService):
    collection_name = "playgrounds"

    def find_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.find({"user_id": user_id})

    def insert_prompt(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        self.insert_one({
            "user_id": user_id,
            "type": data.get("type"),
            "request": data.get("request"),
            "created_at": Database().datetime.now(),
        })