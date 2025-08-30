import random
from pymongo.database import Database
from src.helpers.avatar import generate_avatar
import os

from src.helpers.base_service import BaseService

from src.app.users.dao import UsersDao

class UsersService(BaseService):

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.users_dao = UsersDao(self.db)

    def find_user_by_id(self, user_id: str):
        user = self.users_dao.find_one(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.pop("password", None)
        return user
    
    def find_users(self):
        return self.users_dao.find(projection={"password": 0})

    def update_avatar(self, user_id: str) -> None:
        email = self.find_user_by_id(user_id).get("email")
        img = generate_avatar(email, 800, variant=random.randint(1, 10e16))
        avatar_dir = os.path.join("src", "public", "avatars")
        os.makedirs(avatar_dir, exist_ok=True)
        avatar_path = os.path.join(avatar_dir, f"{user_id}.png")
        img.save(avatar_path, "PNG")