from pydantic import BaseModel


class queryData(BaseModel):
    query: str
