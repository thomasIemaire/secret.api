from deepmerge import always_merger
from transformers import pipeline
import json

from src.app.flows.flows_model import FlowsStepModel
from src.helpers.sardine import Sardine

class FlowManager: 
    _sardine: Sardine
    _supported_documents: list[str]
    _steps: list[FlowsStepModel]
    _raw_result: dict
    _result: list[dict]

    def __init__(self, sardine: Sardine, supported_documents: list[str], steps: list[FlowsStepModel]):
        self._sardine = sardine
        self._supported_documents = supported_documents
        self._steps = steps
        self._raw_result = {}
        self._result = []

    def build_flow_result(self):
        for step in self._steps:
            print(step)
            model_path = f"src/static/agents/{step['agent']['name']}/{step['agent']['version']}"
            with open(f"{model_path}/map.json", "r") as f:
                map_data = f.read()
            self._raw_result = always_merger.merge(self._raw_result, json.loads(map_data))
        print(json.dumps(self._raw_result, ensure_ascii=False))
    
    def run_flow(self):
        if len(self._steps) == 0: return
        
        self.build_flow_result()
        # self._sardine.read_document()

        for page in self._sardine._document._pages:
            if not len(self._supported_documents) == 0 and not page._type in self._supported_documents: continue

            page.read_zone()

            if not page._read or len(page._zones) == 0: continue

            page_result = json.dumps(self._raw_result.copy(), ensure_ascii=False)

            for step in self._steps:
                agent_used = step['agent']
                model_path = f"src/static/agents/{agent_used['name']}/{agent_used['version']}"

                nlp = pipeline(
                    "token-classification",
                    model=model_path,
                    tokenizer="camembert-base",
                    aggregation_strategy="simple"
                )

                test = []
                test2 = []

                for zone in page._zones:
                    flattened = [line for section in zone._content for line in section]
                    text = " ".join(flattened).strip()

                    span_in_zone = {}
                    g_score = 0.0

                    try:
                        doc = nlp(text)

                        for span in doc:

                            if not span["entity_group"] in span_in_zone:
                                span_in_zone[span["entity_group"]] = {
                                    "word": span["word"],
                                    "score": span["score"]
                                }
                                g_score += span["score"]
                            else:
                                if span["score"] > span_in_zone[span["entity_group"]]["score"]:
                                    span_in_zone[span["entity_group"]]["word"] = span["word"]
                                    span_in_zone[span["entity_group"]]["score"] = span["score"]
                                    g_score += span["score"]
                                    g_score -= span_in_zone[span["entity_group"]]["score"]

                            # print(f"Entité : {text_span} | Label : {label} | Confiance : {score}")
                            # page_result = page_result.replace(label, text_span)

                    except Exception as e:
                        print(f"Error processing zone: {zone._type} on page {page._page_number}: {e}")
                        continue

                    test.append(span_in_zone)
                    test2.append(g_score)

                selected_t = test[test2.index(max(test2))]

                for key, value in selected_t.items():
                    page_result = page_result.replace(key, value["word"])
            
            self._result.append(json.loads(page_result))

    def to_dict(self) -> dict:
        return {
            "result": self._result
        }