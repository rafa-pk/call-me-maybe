import sys
import json
from llm_sdk.llm_sdk import Small_LLM_Model 


class Tokeniser:

    def __init__(self) -> None:
        self.llm: Small_LLM_Model = Small_LLM_Model()
        self.tok_to_id: dict[str, str] = self._get_vocab()
        self.merge_rules: dict[tuple[str, str], int] = self._get_merge_rules()

    def _get_vocab(self) -> dict[str, str]:

        try:
            with open(self.llm.get_path_to_vocab_file(), 'r') as file:
                vocab = json.load(file)
            return vocab
        except Exception as error:
            print(f"Tokeniser Error: couldn't read vocab_file: {error}")
            sys.exit(1)

    def _get_merge_rules(self) -> dict[tuple[str, str], int]:
        
        try:
            with open(self.llm.get_path_to_merges_file(), 'r') as file:
                lines = file.read().splitlines()
                merge_rules = [line.split() for line in lines if not line.startswith('#') and line.strip()]
            return {(exp1, exp2): i for i, (exp1, exp2) in enumerate(merge_rules)}
        except Exception as error:
            print(f"Error: error reading merge_rules: {error}")
            sys.exit(1)

    def _tokenise(self, prompt: str) -> list[str]:
      
        prompt = [('Ġ' if char == ' ' else 'Ċ' if char == '\n' else char) for char in prompt]
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
