import random
from pymongo.database import Database
from bson.objectid import ObjectId
from src.helpers.base_service import BaseService
from src.helpers.avatar import generate_avatar
import os

class UsersService(BaseService):
    collection_name = "users"

    def find_user_by_id(self, user_id: str):
        return self.find_one({"_id": ObjectId(user_id)}, projection={"password": 0})

    def update_avatar(self, user_id: str) -> None:
        email = self.find_user_by_id(user_id).get("email")
        img = generate_avatar(email, 800, variant=random.randint(1, 10e16))
        avatar_dir = os.path.join("src", "public", "avatars")
        os.makedirs(avatar_dir, exist_ok=True)
        avatar_path = os.path.join(avatar_dir, f"{user_id}.png")
        img.save(avatar_path, "PNG")