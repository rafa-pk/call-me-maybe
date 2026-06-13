from pydantic import BaseModel


class DataType(BaseModel):

    type: str 


class FunctionDef(BaseModel):

    name: str
    description: str
    parameters: dict[str, DataType]
    returns: DataType
