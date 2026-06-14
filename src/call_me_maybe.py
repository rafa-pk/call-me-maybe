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

    def _constrained_decoding(self, ids: list[int], tokeniser: Tokeniser) -> None:

        # generated_ids = ids
        generated = ""

        while True:
            logits = self.model.get_logits_from_input_ids(ids)
            self._mask_invalid_tokens(generated, logits)
            next_id, next_token = self._pick_best_token(ids, logits)
            generated.append(next_id)
            # last stuff to do
        return generated

    def run(self) -> None:
        context = ("You are a precise function-calling assistant. "
                   "Given a natural language prompt, you must identify the "
                   "correct function name and its arguments, then output "
                   "ONLY a valid JSON object in exactly this format:\n"
                   '{"name": "fn_function_name", "parameters": {"arg1": '
                   'value1, "arg2": value2}}\n\n'
                   "Example:\n"
                   "Prompt: What is the sum of 2 and 3?\n"
                   '{"name": "fn_add_numbers", "parameters": {"a": 2.0, '
                   '"b": 3.0}}\n\n'
                   "Prompt: Greet shrek\n"
                   '{"name": "fn_greet", "parameters": {"name": "shrek"}}\n\n'
                   "Prompt: ")
        functions = self._extract_functions(self.args.functions_definition)
        prompts = self._extract_prompts(self.args.input)
        tokeniser = Tokeniser()

        for prompt in prompts:
            complete_prompt = context + prompt.prompt
            ids = tokeniser.encode(complete_prompt)
            self._constrained_decoding(ids, tokeniser)
        # return json_output