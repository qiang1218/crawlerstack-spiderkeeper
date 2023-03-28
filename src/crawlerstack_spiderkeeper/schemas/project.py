"""
Project schema
"""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import (BaseModel, constr,  # pylint: disable=no-name-in-module
                      validator)

from crawlerstack_spiderkeeper.schemas.base import InDBMixin


class ProjectBase(BaseModel):
    """Project base schema."""
    name: constr(max_length=200) = None
    desc: Optional[str] = None


class Project(ProjectBase, InDBMixin):
    """Project model schema."""
    name: constr(max_length=200)
    # slug: constr(max_length=200)
    create_time: datetime = None
    update_time: datetime = None
    project_id: int = None
    id: int


class ProjectCreate(ProjectBase):
    """Project create schema."""
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
    def check_desc(  # pylint: disable=no-self-use, no-self-argument
            cls,
            value: Optional[str],
            values: Dict[str, Any],
            # **kwargs
    ):
        """
        Check desc.
        :param value:
        :param values:
        :param kwargs:
        :return:
        """
        if not value:
            value = values.get('name')
        return value


class ProjectUpdate(ProjectBase):
    """Project update schema."""
