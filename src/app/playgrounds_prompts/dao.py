from bson import ObjectId

from src.helpers.base_dao import BaseDao

class PlaygroundsPromptsDao(BaseDao):
    collection_name = "playgrounds_prompts"

    def create(self, prompt: dict[str, any]) -> dict[str, any]:
        prompt["created_at"] = self.get_current_time()
        return self.insert_one(prompt)