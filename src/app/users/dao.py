from bson import ObjectId
from src.helpers.base_dao import BaseDao

class UsersDao(BaseDao):
    collection_name = "users"

    def find_one(self, id: str) -> dict | None:
        return self.col.find_one({"_id": ObjectId(id)})