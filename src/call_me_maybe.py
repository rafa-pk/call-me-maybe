import argparse
import json
from pydantic import BaseModel, ConfigDict
from llm_sdk.llm_sdk import Small_LLM_Model


class CallMeMaybe(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)
    args: argparse.Namespace
    model: Small_LLM_Model
    
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args=args, model=Small_LLM_Model())

    def extract_prompts(self, path: str) -> None:

        try:
            with open(path, 'r') as json_prompts:
                raw_file = json_prompts.read()
        except Exception as error:
            print(f"JSon Error: Unable to open {path}: {error}")

    def run(self) -> None:
        # prompts = self.extract_prompts(self.args.input)
        # functions = self.extract_functions(self.args.function_definition)
        print(self.args)
        print(self.model._model_name)