from bson import ObjectId
from pymongo.database import Database

from src.helpers.base_service import BaseService

from src.app.playgrounds_prompts.dao import PlaygroundsPromptsDao
from src.app.playgrounds.dao import PlaygroundsDao

class PlaygroundsPromptsService(BaseService):

    def __init__(self, db: Database):
        super().__init__(db)
        self.playgrounds_prompts_dao = PlaygroundsPromptsDao(db)
        self.playgrounds_dao = PlaygroundsDao(db)

    def find_prompt_by_id(self, prompt_id: str):
        prompt = self.playgrounds_prompts_dao.find_one({"_id": ObjectId(prompt_id)})

        if not prompt:
            raise ValueError("Prompt not found")
        
        return prompt

    def find_prompts_by_playground_id(self, playground_id: str):
        return self.playgrounds_prompts_dao.find({"playground": ObjectId(playground_id)})

    def create_prompt(self, playground_id: str, data: dict[str, any]) -> dict[str, any]:
        playground = self.playgrounds_dao.find_one({"_id": ObjectId(playground_id)})

        if not playground:
            raise ValueError("Playground not found")

        if not data.get("content") or not data.get("system"):
            raise ValueError("Prompt content and system are required")
        
        return self.playgrounds_prompts_dao.create({
            "playground": ObjectId(playground_id),
            "content": data["content"],
            "system": {**data.get("system", {}), "evaluation": 0},
            "created_by": ObjectId(data.get("created_by")),
        })

    def delete_prompt(self, prompt_id: str) -> None:
        self.find_prompt_by_id(prompt_id)
        self.playgrounds_prompts_dao.delete_one({"_id": ObjectId(prompt_id)})

    def like_prompt(self, prompt_id: str) -> None:
        prompt = self.find_prompt_by_id(prompt_id)

        if prompt.get("system", {}).get("evaluation") == 1:
            self.reset_prompt_evaluation(prompt_id)
        
        self.update_evaluation(prompt_id, 1)

    def dislike_prompt(self, prompt_id: str) -> None:
        prompt = self.find_prompt_by_id(prompt_id)

        if prompt.get("system", {}).get("evaluation") == -1:
            self.reset_prompt_evaluation(prompt_id)

        self.update_evaluation(prompt_id, -1)

    def reset_prompt_evaluation(self, prompt_id: str) -> None:
        self.update_evaluation(prompt_id, 0)
        raise ValueError("Prompt evaluation reset to neutral")

    def update_evaluation(self, prompt_id: str, evaluation: int) -> None:
        self.playgrounds_prompts_dao.update_one({"_id": ObjectId(prompt_id)}, {"system.evaluation": evaluation})