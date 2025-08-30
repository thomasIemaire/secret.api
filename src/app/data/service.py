from pymongo.database import Database
from bson.objectid import ObjectId
from src.helpers.base_service import BaseService

from .dao import DataDao


class DataService(BaseService):

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.data_dao = DataDao(db)

    def find_one_by_id(self, id: str) -> dict | None:
        return self.data_dao.find_one({"_id": ObjectId(id)})

    def create(self, user_id: str, data: dict) -> dict:
        doc = {
            "name": data.get("name"),
            "data": data.get("data"),
            "created_at": self.data_dao.get_current_time(),
            "created_by": ObjectId(user_id),
        }

        return self.data_dao.insert_one(doc)
