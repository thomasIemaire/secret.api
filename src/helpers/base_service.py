from pymongo.database import Database

class BaseService:
    def __init__(self, db: Database) -> None:
        self.db = db
