from typing import Any, Dict
from pymongo.database import Database
from bson.objectid import ObjectId

from src.helpers.base_service import BaseService

from src.app.playgrounds.dao import PlaygroundsDao


class PlaygroundsService(BaseService):

    def __init__(self, db: Database):
        super().__init__(db)
        self.playground_dao = PlaygroundsDao(db)

    def find_by_user_id(self, user_id: str):
        return self.playground_dao.find_playgrounds_for_user(user_id)

    def create_playground(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get("name"):
            raise ValueError("Playground name is required")
        playground = {
            "created_by": ObjectId(user_id),
            "name": data["name"],
            "shared_with": data.get("shared_with", []),
        }
        return self.playground_dao.create(playground)
