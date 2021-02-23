from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, constr, validator


class ProjectBase(BaseModel):
    name: constr(max_length=200) = None
    desc: Optional[str] = None


class Project(ProjectBase):
    name: constr(max_length=200)
    # slug: constr(max_length=200)
    create_time: datetime = None
    update_time: datetime = None
    project_id: int = None
    id: int

    class Config:
        orm_mode = True


class ProjectCreate(ProjectBase):
    name: constr(max_length=200)
    # slug: constr(max_length=200)
    #
    # @validator('slug')
    # def check_name(cls, v: str):
    #     """
    #     Slug must lower and `-` ==> `_`
    #     eg: `hello_world` is fine, not pass `hello-world` or `hello world`
    #     :param v:
    #     :return:
    #     """
    #     check_character = ['-', ' ']
    #     for character in check_character:
    #         if character in v:
    #             raise ValueError(f'"{character}" must not contain in name')
    #     if not v.islower():
    #         raise ValueError('name must lower')
    #     return v

    @validator('desc')
    def check_desc(cls, v: Optional[str], values: Dict[str, Any], **kwargs):
        if not v:
            v = values.get('name')
        return v


class ProjectUpdate(ProjectBase):
    pass
