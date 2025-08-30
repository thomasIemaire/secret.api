from bson import ObjectId

from src.helpers.base_dao import BaseDao

class PlaygroundsDao(BaseDao):
    collection_name = "playgrounds"

    def find_playgrounds_for_user(self, user_id: str):
        return self.find({
            "$or": [
                {"created_by": ObjectId(user_id)},
                {"shared_with": ObjectId(user_id)}
            ]
        })
    
    def create(self, playground: any):
        playground["created_at"] = self.get_current_time()
        return self.insert_one(playground)