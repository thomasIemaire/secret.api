import os

class AgentsService:

    base_path = "src/static/agents"

    def __init__(self, db):
        pass

    def get_agents(self):
        agents_list = []

        if not os.path.exists(self.base_path):
            return agents_list

        for agent_name in os.listdir(self.base_path):
            agent_path = os.path.join(self.base_path, agent_name)
            if os.path.isdir(agent_path):
                versions = [
                    version_name.split('.pt')[0] for version_name in os.listdir(agent_path)
                ]
                agents_list.append({
                    "agent": agent_name,
                    "versions": versions
                })

        return agents_list