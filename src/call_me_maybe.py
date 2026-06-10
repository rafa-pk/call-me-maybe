import argparse
from pydantic import BaseModel, ConfigDict
from llm_sdk.llm_sdk import Small_LLM_Model


class CallMeMaybe(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)
    args: argparse.Namespace
    model: Small_LLM_Model
    
    def __init__(self, args: argparse.Namespace) -> None:
        super().__init__(args=args, model=Small_LLM_Model())

    def extract_prompts(path: str) -> None:
        # 

    def run(self) -> None:
        self.extract_prompts(self.args.input)
        print(self.args)
        print(self.model._model_name)