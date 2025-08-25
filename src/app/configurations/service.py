from pymongo.database import Database
from bson.objectid import ObjectId
from src.helpers.base_service import BaseService
import random, re

class ConfigurationsService(BaseService):
    collection_name = "configurations"

    def find_all(self) -> list[dict]:
        return self.find(sort=[("created_at", -1)], projection={"attributes": 0, "formats": 0, "randomizers": 0})

    def find_one_by_id(self, id: str) -> dict | None:
        return self.find_one({"_id": ObjectId(id)})

    def create(self, user_id: str, data: dict) -> dict:
        doc = {
            "name": data.get("name"),
            "description": data.get("description"),
            "attributes": data.get("attributes", []),
            "formats": data.get("formats", []),
            "randomizers": data.get("randomizers", []),
            "created_by": ObjectId(user_id),
            "created_at": self.get_current_time(),
            "possibilities": self.calculate_max_configuration_possibilities(data)
        }

        self.insert_one(doc)

        return self.serialize(doc)
    
    def calculate_max_configuration_possibilities(
            self,
            configuration: dict
        ) -> int:
        possibilities = 1

        for attr in configuration.get("attributes", []):
            vattr = attr.get("value")
            possibilities *= (self._calculate_attribute_size(
                vattr.get("rule", ""),
                vattr.get("parameters", {})
            ) * attr.get("frequency", 1))

        return possibilities * len(configuration.get("formats", []))
    
    def _calculate_attribute_size(
        self,
        rule: str,
        parameters: dict
    ):
        match rule:
            case "randint":
                vmin = int(parameters.get("min", 0))
                vmax = int(parameters.get("max", 0))
                if vmin > vmax: vmin, vmax = vmax, vmin
                return abs(vmin) + vmax
            case "data":
                data_id = parameters.get("object_id")
                data = None
                if data_id:
                    data = self.db["configurations_data"].find_one({"_id": ObjectId(data_id)})
                return len(data.get("data", [])) if data else 1
            case "configuration":
                config_id = parameters.get("object_id")
                if config_id:
                    configuration = self.find_one({"_id": ObjectId(config_id)})
                    size = self.calculate_max_configuration_possibilities(configuration)
                return size
            case _:
                return 1
