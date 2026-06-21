import argparse
import json
import sys
import re
from typing import Any
from pydantic import BaseModel, ConfigDict
from llm_sdk.llm_sdk import Small_LLM_Model
from src.validation_classes import FunctionDef, Prompt, DataType
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

        existing_ids: list[int] = generated_ids.copy()
        fn_name_str: str = ""
        fn_name_ids: list[int] = []
        initial_quotes: list[int] = self.tokeniser.encode('"')

        fn_name_str += '"'
        fn_name_ids += initial_quotes
        existing_ids += initial_quotes
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

    def _generate_num(self, existing_ids: list[int]) -> list[int]:

        value_id: list[int] = []
        value_str: str = ""
        total_ids: list[int] = existing_ids.copy()

        while True:
            logits = self.model.get_logits_from_input_ids(total_ids)
            unconstrained_choice = int(logits.index(max(logits)))
            unconstrained = self.tokeniser.id_to_tok[unconstrained_choice].replace("Ġ", " ").replace("Ċ", "\n")
            if re.fullmatch(r"-?\d*\.?\d*", value_str + unconstrained) is None and value_str != "":
                break
            for tok_id in range(len(logits)):
                tok_str = self.tokeniser.id_to_tok.get(tok_id)
                if tok_str is None:
                    logits[tok_id] = float("-inf")
                    continue
                token_str = tok_str.replace("Ġ", " ").replace("Ċ", "\n")
                candidate = value_str + token_str
                if re.fullmatch(r"-?\d*\.?\d*", candidate) is None and value_str != "":
                    logits[tok_id] = float("-inf")
            next_id = int(logits.index(max(logits)))
            value_id.append(next_id)
            total_ids.append(next_id)
            value_str += self.tokeniser.id_to_tok[next_id].replace("Ġ", " ").replace("Ċ", "\n")
        return value_id

    def _generate_str(self, existing_ids: list[int]) -> list[int]:

        str_id: list[int] = []
        str_str: str = ""
        total_ids: list[int] = existing_ids.copy()
        initial_quotes: list[int] = self.tokeniser.encode('"')
        
        str_str += '"'
        str_id += initial_quotes
        total_ids += initial_quotes
        while True:
            logits = self.model.get_logits_from_input_ids(total_ids)
            for tok_id in range(len(logits)):
                tok_str = self.tokeniser.id_to_tok.get(tok_id)
                if tok_str is None:
                    logits[tok_id] = float("-inf")
                    continue
                token_str = tok_str.replace("Ġ", " ").replace("Ċ", "\n")
                if token_str != '"' and any(c in token_str for c in '{}[]'):
                    logits[tok_id] = float("-inf") 
            next_id = int(logits.index(max(logits)))
            next_str = self.tokeniser.id_to_tok[next_id].replace("Ġ", " ").replace("Ċ", "\n")
            str_id.append(next_id)
            total_ids.append(next_id)
            str_str += next_str
            if next_str.endswith('"'):
                break
        return str_id

    def _generate_bool(self, existing_ids: list[int]) -> list[int]:

        bool_id: list[int] = []
        bool_str: str = ""
        total_ids: list[int] = existing_ids.copy()

        while True:
            logits = self.model.get_logits_from_input_ids(total_ids)
            for tok_id in range(len(logits)):
                tok_str = self.tokeniser.id_to_tok.get(tok_id)
                if tok_str is None:
                    logits[tok_id] = float("-inf")
                    continue
                token_str = tok_str.replace("Ġ", " ").replace("Ċ", "\n")
                candidate = bool_str + token_str
                if not (("true".startswith(candidate)) or ("false".startswith(candidate))):
                    logits[tok_id] = float("-inf")
            next_id = int(logits.index(max(logits)))
            bool_id.append(next_id)
            total_ids.append(next_id)
            bool_str += self.tokeniser.id_to_tok[next_id].replace("Ġ", " ").replace("Ċ", "\n")
            if bool_str in ["true", "false"]:
                break
        return bool_id
    
    def _generate_val(self, existing_ids: list[int], arg_type: str) -> list[int]:

        if arg_type == "number":
            return self._generate_num(existing_ids)
        elif arg_type == "string":
            return self._generate_str(existing_ids)
        elif arg_type == "bool":
            return self._generate_bool(existing_ids)

    def _generate_params(self, generated_ids: list[int], fn_name: str, functions: dict[str, FunctionDef]) -> list[int]:

        existing_ids: list[int] = generated_ids.copy()
        params: dict[str, DataType] = functions[fn_name].parameters
        params_ids: list[int] = []

        for i, (arg_name, arg_type) in enumerate(params.items()):
            param = self.tokeniser.encode(f'"{arg_name}": ')
            existing_ids += param
            params_ids += param
            val = self._generate_val(existing_ids, arg_type.type)
            existing_ids += val
            params_ids += val
            if i < len(params) - 1:
                comma = self.tokeniser.encode(', ')
                existing_ids += comma
                params_ids += comma 
        return params_ids

    def _constrained_decoding(self, ids: list[int], functions: dict[str, FunctionDef]) -> dict[str, Any]:

        prompt_len = len(ids)
        generated_ids: list[int] = ids + self.tokeniser.encode('{"name": ')
        try:
            fn_name_id: list[int] = self._generate_fn_name(generated_ids, functions)
        except Exception as error:
            print(f"Error generating function name: {error}")
            sys.exit(1)
        generated_ids += fn_name_id
        fn_name = self.tokeniser.decode(fn_name_id)
        generated_ids += self.tokeniser.encode('", "parameters": {')
        try:
            generated_ids += self._generate_params(generated_ids, fn_name, functions)
        except Exception as error:
            print(f"Error generating function parameters: {error}")
            sys.exit(1)
        generated_ids += self.tokeniser.encode("}}")
        generated = self.tokeniser.decode(generated_ids[prompt_len:])
        print(generated)
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