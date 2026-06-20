import argparse
import json
import sys
from typing import Any
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

    def _generate_fn_name(self, generated_ids: list[int]) -> list[int]:

            logits = self.llm.get_logits_from_input_ids(generated_ids)

            # Generation logic

        return fn_name

    def _constrained_decoding(self, ids: list[int], tokeniser: Tokeniser) -> dict[str, Any]:

        generated_ids = ids + tokeniser.encode('{"name": "')
        fn_name_id = self._generate_fn_name(generated_ids)
        # generated_ids += fn_name_id
        # fn_name = tokeniser.decode(fn_name_id)
        # generated_ids += tokeniser.encode('", {"parameters": {"')
        # generated_ids += self._generate_params(generated_ids, fn_name)
        # generated_ids += tokeniser.encode("}}")
        generated = tokeniser.decode(generated_ids)
        # return json.loads(generated)

    def run(self) -> None:

        functions = self._extract_functions(self.args.functions_definition)
        prompts = self._extract_prompts(self.args.input)
        context = ("You are a precise function-calling assistant. "
                   "Given a natural language prompt, you must identify the "
                   "correct function name and its arguments, then output "
                   "ONLY a valid JSON object in exactly this format:\n"
                   '{"name": "fn_function_name", "parameters": {"arg1": '
                   'value1, "arg2": value2}}\n\n'
                   "Available functions: \n"
                   f"{functions}"
                   "\nExample:\n"
                   "Prompt: What is the sum of 2 and 3?\n"
                   '{"name": "fn_add_numbers", "parameters": {"a": 2.0, '
                   '"b": 3.0}}\n\n'
                   "Prompt: Greet shrek\n"
                   '{"name": "fn_greet", "parameters": {"name": "shrek"}}\n\n'
                   "My Prompt: ")
        tokeniser = Tokeniser()
        # output = []

        for prompt in prompts:
            complete_prompt = context + prompt.prompt + '\n'
            ids = tokeniser.encode(complete_prompt)
            # entry = {"prompt": prompt.prompt}
            # entry.update(
            self._constrained_decoding(ids, tokeniser)  # )
            # output.append(entry)
        # self._create_output_file(output)