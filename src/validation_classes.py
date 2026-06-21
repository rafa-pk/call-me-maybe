from pydantic import BaseModel
from typing import Literal


class Prompt(BaseModel):

    prompt: str


class DataType(BaseModel):

    type: Literal["number", "string", "bool"] 


class FunctionDef(BaseModel):

    name: str
    description: str
    parameters: dict[str, DataType]
    returns: DataType
