import sys
import json
import ast
from llm_sdk.llm_sdk import Small_LLM_Model 


class Tokeniser:

    def __init__(self) -> None:
        self.llm: Small_LLM_Model = Small_LLM_Model()
        self.vocab_path: str = self.llm.get_path_to_vocab_file() 
        self.tok_to_id = self._get_vocab()
        self.merge_rules = self._get_merge_rules()

    def _get_vocab(self) -> dict[str, str]:

        try:
            with open(self.vocab_path, 'r') as file:
                vocab = json.load(file)
            return vocab
        except Exception as error:
            print(f"Tokeniser Error: couldn't read vocab_file: {error}")
            sys.exit(1)

    def _get_merge_rules(self) -> dict[tuple[str, str], int]:
        try:
            with open("src/merge_rules.txt", 'r') as file:
                merge_rules = ast.literal_eval(file.read())
            return {(ch1, ch2): i for i, (ch1, ch2) in enumerate(merge_rules)}
        except Exception as m:
            print(f"Error: error reading merge_rules: {m}")
            sys.exit(1)

    def _tokenise(self, prompt: str) -> list[str]:
       
        prompt = [('Ġ' if char == ' ' else char)for char in prompt]
        while True:
            priority = float("inf")
            best_pair = None

            for i in range(len(prompt) - 1):
                pair = (prompt[i], prompt[i + 1])
                if pair in self.merge_rules:
                    index = self.merge_rules[pair]
                    if index < priority:
                        priority = index
                        best_pair = pair
            if best_pair is None:
                break
            t1, t2 = best_pair
            new_prompt = []
            i = 0
            while i < len(prompt):
                if i < len(prompt) - 1 and prompt[i] == t1 and prompt[i + 1] == t2:
                    new_prompt.append(t1 + t2)
                    i += 2
                else:
                    new_prompt.append(prompt[i])
                    i += 1
            prompt = new_prompt
        return prompt

    def encode(self, prompt: str) -> list[int]:
        try:
            tokens = self._tokenise(prompt)
        except Exception as error:
            print(f"Tokenisation Error: {error}")
            sys.exit(1)
        
        ids = []
        for token in tokens:
            ids.append(self.tok_to_id[token])
        return ids