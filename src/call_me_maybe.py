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
    tokeniser: Tokeniser
    
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args=args, model=Small_LLM_Model(), tokeniser=Tokeniser())

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

    def _generate_fn_name(self, generated_ids: list[int], functions: dict[str, FunctionDef]) -> list[int]:

        existing_ids = generated_ids.copy()
        fn_name_str: str = ""
        fn_name_ids: list[int] = []

        while True:
            logits = self.model.get_logits_from_input_ids(existing_ids)
            for tok_id in range(len(logits)):
                tok_str = self.tokeniser.id_to_tok.get(tok_id)
                if tok_str is None:
                    logits[tok_id] = float("-inf")
                    continue
                token_str = tok_str.replace("Ġ", " ").replace("Ċ", "\n")
                candidate = fn_name_str + token_str
                if not any(name.startswith(candidate) for name in functions):
                    logits[tok_id] = float("-inf")
            next_id = int(logits.index(max(logits)))
            fn_name_ids.append(next_id)
            existing_ids.append(next_id)
            fn_name_str += self.tokeniser.id_to_tok[next_id].replace("Ġ", " ").replace("Ċ", "\n")
            if fn_name_str in functions:
                break
        return fn_name_ids

    # def _generate_params(generated_ids: list[int], fn_name: str, functions: dict[str, FunctionDef]) -> list[int]:

    #    existing_ids = generated_ids.copy()

    #    for 

    def _constrained_decoding(self, ids: list[int], functions: dict[str, FunctionDef]) -> dict[str, Any]:

        prompt_len = len(ids)
        generated_ids: list[int] = ids + self.tokeniser.encode('{"name": "')
        try:
            fn_name_id: list[int] = self._generate_fn_name(generated_ids, functions)
        except Exception as error:
            print(f"Error generating function name: {error}")
            sys.exit(1)
        generated_ids += fn_name_id
        fn_name = self.tokeniser.decode(fn_name_id)
        generated_ids += self.tokeniser.encode('", "parameters": {"')
        # try:
        #    generated_ids += self._generate_params(generated_ids, fn_name, functions)
        # except Exception as error:
        #    print(f"Error generating function parameters: {error}")
        #    sys.exit(1)
        generated_ids += self.tokeniser.encode("}}")
        generated = self.tokeniser.decode(generated_ids[prompt_len:])
        # return json.loads(generated)

    def run(self) -> None:

        functions: dict[str, FunctionDef] = self._extract_functions(self.args.functions_definition)
        prompts: list[Prompt] = self._extract_prompts(self.args.input)
        context: str = ("You are a precise function-calling assistant. "
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
        # output = []

        for prompt in prompts:
            complete_prompt = context + prompt.prompt + '\n'
            ids = self.tokeniser.encode(complete_prompt)
            # entry = {"prompt": prompt.prompt}
            # entry.update(
            self._constrained_decoding(ids, functions)  # )
            # output.append(entry)
        # self._create_output_file(output)