from pydantic import BaseModel


class InDBMixin(BaseModel):
    id: int

    class Config:
        orm_mode = True
