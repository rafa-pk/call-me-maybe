import argparse
import json
from pydantic import BaseModel, ConfigDict
from llm_sdk.llm_sdk import Small_LLM_Model
from src.validation_classes import FunctionDef


class CallMeMaybe(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)
    args: argparse.Namespace
    model: Small_LLM_Model
    
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args=args, model=Small_LLM_Model())

    def _extract_json(self, path: str) -> dict[str, any]:

        try:
            with open(path, 'r') as file:
                json_file = json.load(file)
        except Exception as error:
            print(f"JSon Error: Unable to open {path}: {error}")
        return (json_file)

    def _extract_functions(self, function_defs: str) -> dict[str, FunctionDef]:

        raw_functions = self._extract_json(function_defs)
        return {func["name"]: FunctionDef(**func) for func in raw_functions}

    def run(self) -> None:
        # self.extract_prompts(self.args.input)
        functions = self._extract_functions(self.args.function_definition)
        print(functions)
        print(self.args)
        print(self.model._model_name)