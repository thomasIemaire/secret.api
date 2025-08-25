from typing import Literal, Optional
from pymongo.database import Database
from bson.objectid import ObjectId
from src.app.configurations.service import ConfigurationsService
from src.helpers.base_service import BaseService
import copy, random, uuid, re

class ModelsService(BaseService):
    collection_name = "models"

    def find_all(self) -> list[dict]:
        return self.find(sort=[("updated_at", -1)], projection={"mapper": 0, "parameters": 0, "configuration": 0})

    def create(self, user_id: str, model_data: dict) -> ObjectId:
        doc = {
            "name": model_data.get("name", "Untitled Model"),
            "description": model_data.get("description", ""),
            "reference": model_data.get("reference", ""),
            "version": model_data.get("version", "1.0"),
            "mapper": model_data.get("mapper", {}),
            "parameters": model_data.get("parameters", {}),
            "created_by": ObjectId(user_id),
            "updated_by": ObjectId(user_id),
            "created_at": self.get_current_time(),
            "updated_at": self.get_current_time(),
            "status": "wainting",
        }

        self.col.insert_one(doc)

        return self.serialize(doc)
    
    def build_model(self, model_id: str) -> dict:
        model = self.find_one({"_id": ObjectId(model_id)})
        if not model:
            raise ValueError("Model not found")
        
        ments = model.get("entities", {})
        mkeys = list(ments.values())
        
        mcid = model.get("configuration", None)
        if not mcid:
            raise ValueError("Model configuration is missing")
        
        configuration = ConfigurationsService(db=self.db).find_one({"_id": ObjectId(mcid)})
        if not configuration:
            raise ValueError("Model configuration not found")
        
        mpar = model.get("parameters", {})

        dataset = []
        seed = str(uuid.uuid4())
        chunk_size = 5*1e3

        for _ in range(mpar.get("dataset_size", 1e5)):
            print(_)

            mvb = self.build_model_configuration(copy.deepcopy(configuration))

            mrd = random.choice(model.get("randomizers", []))
            if mrd and mrd.get("frequency", 0) >= random.random():
                mvb = self.build_model_configuration_randomizers(mvb)
            
            dataset.append(
                self.build_model_entity(
                    mvb,
                    mkeys,
                    {v:k for k,v in ments.items()}
                )
            )

            print(mvb.get("value", ""), dataset[-1])

    def build_model_configuration(self, configuration: dict) -> dict:
        print(configuration)

        catt = configuration.get("attributes")
        cfmt = configuration.get("formats")

        sfmt = random.choice(cfmt)
        satt = []

        for attr in catt:
            kattr = attr.get("key")
            fattr = attr.get("frequency", 1)
            rattr = attr.get("requirements", [])

            vattr = attr.get("value") if fattr > random.random() else False

            if isinstance(vattr, dict):
                tvattr = vattr.get("type")
                rvattr = vattr.get("rule")
                pvattr = vattr.get("parameters", {})
                bvattr, bcattrs = self.build_model_configuration_value(tvattr, rvattr, pvattr)

                print(bvattr, bcattrs)

                if bcattrs:
                    for bcattr in bcattrs:
                        satt.append(bcattr)
            
            satt.append({
                "key": kattr,
                "value": bvattr if vattr else '',
                "requirements": self.build_model_configuration_requirements(bvattr, rattr) if vattr else True
            })

            print(satt[-1])

        bfmt = self.build_model_configuration_format(sfmt, satt)
        configuration['attributes'] = satt
        configuration['value'] = re.sub(r'\s+', ' ', bfmt.strip())

        return configuration

    def build_model_configuration_value(
        self,
        vtype: Literal["number", "string"],
        rule: str,
        parameters: dict
    ) -> Optional[int | str]:
        value = None

        match rule:
            case "randint":
                vmin = int(parameters.get("min", 0))
                vmax = int(parameters.get("max", 100))
                if vmin > vmax: vmin, vmax = vmax, vmin
                value = random.randint(vmin, vmax)

            case "data":
                data_id = parameters.get("object_id", [])
                data = self.db["data"].find_one({"_id": ObjectId(data_id)})
                value = random.choice(data.get("values", []))

            case "configuration":
                config_id = parameters.get("object_id")
                config = self.db["models"].find_one({"_id": ObjectId(config_id)})
                value = self.build_model_configuration(config.get("configuration", {}))
        
        if value is None: return None
            
        return self.build_model_configuration_vtype(vtype, value), None
    
    def build_model_configuration_vtype(
        self,
        vtype: Literal["number", "string"],
        value: any
    ) -> Optional[int | str]:
        match vtype:
            case "number":
                try:
                    return int(value)
                except:
                    return str(value)
            case _:
                return str(value)

    def build_model_configuration_requirements(
        self,
        value: any,
        requirements: list[dict]
    ) -> bool:
        for req in requirements:
            rreq = req.get("rule")
            creq = req.get("constraint")

            match rreq:
                case "regex":
                    if not re.match(creq, str(value)):
                        return False
                case "eq":
                    if str(value) != str(creq):
                        return False
                case "neq":
                    if str(value) == str(creq):
                        return False
                case "gt":
                    try:
                        if float(value) <= float(creq):
                            return False
                    except: pass
                case "lt":
                    try:
                        if float(value) >= float(creq):
                            return False
                    except: pass
                case "gte":
                    try:
                        if float(value) < float(creq):
                            return False
                    except: pass
                case "lte":
                    try:
                        if float(value) > float(creq):
                            return False
                    except: pass
                case "in":
                    if str(value) not in map(str, creq):
                        return False
                case "nin":
                    if str(value) in map(str, creq):
                        return False
                case _:
                    pass
                    
        return True

    def build_model_configuration_format(
        self,
        format: str,
        attributes: list[dict]
    ) -> str:
        for attr in attributes:
            kattr = attr.get("key")
            vattr = attr.get("value", "")
            format = format.replace(f"{{{kattr}}}", str(vattr))
        return format
    
    def build_model_entity(
        self,
        configuration: dict,
        keys: list[str],
        map: dict
    ) -> dict:
        vfmt = configuration.get("value", "")
        ents = []

        for attr in configuration.get("attributes", []):
            kattr = attr.get("key")
            vattr = attr.get("value", "")
            rattr = attr.get("requirements", True)


            if not kattr in keys or \
               vattr == '' or not rattr:
                continue

            enttok = map.get(kattr)

            sta = vfmt.lower().find(vattr.lower())
            if sta == -1: continue
            end = sta + len(vattr)

            ents.append([sta, end, enttok])
        
        return { "text": vfmt, "entities": ents }