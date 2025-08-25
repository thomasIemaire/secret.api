from pymongo.database import Database
from bson.objectid import ObjectId
from src.helpers.base_service import BaseService

class DataService(BaseService):
    collection_name = "models_data"
