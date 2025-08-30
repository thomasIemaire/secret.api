from typing import Any, Dict
from pymongo.database import Database
from bson.objectid import ObjectId
from src.helpers.base_service import BaseService
from src.helpers.avatar import generate_avatar
from flask_jwt_extended import create_access_token, create_refresh_token
import hashlib, base64, uuid, hmac, os

from .dao import AuthDao


class AuthService(BaseService):

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_dao = AuthDao(db)

    def find(self, query=None, *, projection={"password": 0, "apikey": 0}, sort=None, limit=None, skip=0):
        return self.auth_dao.find(query, projection=projection, sort=sort, limit=limit, skip=skip)

    def generate_apikey(self) -> str:
        return str(uuid.uuid4())

    def b64url(self, bytes: bytes) -> bytes:
        return base64.urlsafe_b64encode(bytes)

    def hash_password(self, password: str, apikey: str) -> str:
        dk = hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), self.b64url(uuid.UUID(apikey).bytes), 269_874)
        return base64.b64encode(dk).decode("ascii")

    def verify_password(self, password: str, hashed_password: str, apikey: str) -> bool:
        return hmac.compare_digest(self.hash_password(password, apikey), hashed_password)

    def register(self, data: Dict[str, Any]) -> Dict[str, Any]:
        email = (data.get("email") or "").strip().lower()

        if not email or "@" not in email:
            raise ValueError("Email invalide")

        if self.auth_dao.find_one({"email": email}):
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
            "role": "user",
        }

        user = self.auth_dao.insert_one(user)

        img = generate_avatar(email, 800)
        avatar_dir = os.path.join("src", "public", "avatars")
        os.makedirs(avatar_dir, exist_ok=True)
        avatar_path = os.path.join(avatar_dir, f"{user['_id']}.png")
        img.save(avatar_path, "PNG")

        token, refresh = self.token(user=user)
        user.pop("password", None)

        return {"token": token, "refresh_token": refresh, "user": user}

    def login(self, data: Dict[str, Any]) -> Dict[str, Any]:
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        if not email or not password:
            raise ValueError("Email et password requis")

        user = self.auth_dao.find_one({"email": email})
        if not user or not self.verify_password(password, user["password"], user["apikey"]):
            raise ValueError("Email ou mot de passe invalide")

        user.pop("password", None)

        token, refresh = self.token(user=user)

        return {"token": token, "refresh_token": refresh, "user": user}
    
    def token(self, *, user_id: str = None, user: Dict[str, Any]) -> tuple:
        if not user:
            user = self.auth_dao.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("Utilisateur introuvable")
        
        user_id = str(user["_id"])

        token = create_access_token(identity=user_id, additional_claims={"role": user.get("role", 1)})
        refresh = create_refresh_token(identity=user_id)

        return (token, refresh)
    
    def login_token(self, user_id: str) -> Dict[str, Any]:
        user = self.auth_dao.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("Utilisateur introuvable")
        
        user.pop("password", None)
        token, refresh = self.token(user=user)

        return {"token": token, "refresh_token": refresh, "user": user}

    def email_exists(self, email: str) -> bool:
        email = email.strip().lower()
        return self.auth_dao.find_one({"email": email}) is not None
