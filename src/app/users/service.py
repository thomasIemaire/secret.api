import random
from typing import Any, Dict, List, Optional
from pymongo.database import Database
from bson.objectid import ObjectId
from src.helpers.base_service import BaseService
from src.helpers.avatar import generate_avatar
import hashlib, base64, uuid, hmac, os

class UsersService(BaseService):
    collection_name = "users"

    def find(self, query = None, *, projection = {"password": 0, "apikey": 0}, sort = None, limit = None, skip = 0):
        return super().find(query, projection=projection, sort=sort, limit=limit, skip=skip)

    def generate_apikey(self) -> str:
        return str(uuid.uuid4())

    def _salt(self, apikey: str) -> bytes:
        return base64.urlsafe_b64encode(uuid.UUID(apikey).bytes)

    def hash_password(self, password: str, apikey: str) -> str:
        dk = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), self._salt(apikey), 269_874)
        return base64.b64encode(dk).decode("ascii")

    def verify_password(self, password: str, hashed_password: str, apikey: str) -> bool:
        return hmac.compare_digest(self.hash_password(password, apikey), hashed_password)

    def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        email = (data.get("email") or "").strip().lower()

        if not email or "@" not in email:
            raise ValueError("Email invalide")

        if self.find_one({"email": email}):
            raise ValueError("Email déjà utilisé")

        if not data.get("firstname") or not data.get("lastname"):
            raise ValueError("First name et last name requis")
        if not data.get("password"):
            raise ValueError("Password requis")

        apikey = self.generate_apikey()
        user = {
            "email": email,
            "firstname": data["firstname"],
            "lastname": data["lastname"],
            "apikey": apikey,
            "password": self.hash_password(data["password"], apikey),
            "role": 1,
        }

        self.insert_one(user)

        img = generate_avatar(email, 800)
        avatar_dir = os.path.join("src", "public", "avatars")
        os.makedirs(avatar_dir, exist_ok=True)
        avatar_path = os.path.join(avatar_dir, f"{user['_id']}.png")
        img.save(avatar_path, "PNG")

        return self.find_one({"_id": user["_id"]}, projection={"_id": 0, "password": 0})

    def signin(self, data: Dict[str, Any]) -> Dict[str, Any]:
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        if not email or not password:
            raise ValueError("Email et password requis")

        user = self.find_one({"email": email})
        if not user or not self.verify_password(password, user["password"], user["apikey"]):
            raise ValueError("Email ou mot de passe invalide")

        user.pop("password", None)
        return user

    def update_avatar(self, user_id: str) -> None:
        email = self.find_one({"_id": ObjectId(user_id)}).get("email")
        img = generate_avatar(email, 800, variant=random.randint(1, 10e16))
        avatar_dir = os.path.join("src", "public", "avatars")
        os.makedirs(avatar_dir, exist_ok=True)
        avatar_path = os.path.join(avatar_dir, f"{user_id}.png")
        img.save(avatar_path, "PNG")