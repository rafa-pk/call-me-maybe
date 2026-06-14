from pydantic import BaseModel


class Prompt(BaseModel):

    prompt: str


class DataType(BaseModel):

    type: str 


class FunctionDef(BaseModel):

    name: str
    description: str
    parameters: dict[str, DataType]
    returns: DataType
