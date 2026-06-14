import argparse
import json
import sys
from pydantic import BaseModel, ConfigDict
from llm_sdk.llm_sdk import Small_LLM_Model
from src.validation_classes import FunctionDef, Prompt
from src.tokeniser import Tokeniser


class CallMeMaybe(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)
    args: argparse.Namespace
    model: Small_LLM_Model
    
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args=args, model=Small_LLM_Model())

    def _extract_functions(self, function_defs: str) -> dict[str, FunctionDef]:

        try:
            with open(function_defs, 'r') as file:
                raw_functions = json.load(file)
            return {func["name"]: FunctionDef(**func) for func in raw_functions}
        except Exception as error:
            print(f"JSon Error: {function_defs}: {error}")
            sys.exit(1) 

    def _extract_prompts(self, prompts: str) -> list[Prompt]:

        try:
            with open(prompts, 'r') as file:
                raw_functions = json.load(file)
            return [Prompt(**prompt) for prompt in raw_functions]
        except Exception as error:
            print(f"JSon Error: {prompts}: {error}")
            sys.exit(1)

    def run(self) -> None:
        functions = self._extract_functions(self.args.functions_definition)
        prompts = self._extract_prompts(self.args.input)
        tokeniser = Tokeniser()

        for prompt in prompts:
            ids = tokeniser.encode(prompt.prompt)
            logits = self.model.get_logits_from_input_ids(ids)