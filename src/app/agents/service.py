from typing import Any, Dict, List, Optional
from pymongo.database import Database
from src.helpers.base_service import BaseService

class AgentsService(BaseService):
    collection_name = "agents"