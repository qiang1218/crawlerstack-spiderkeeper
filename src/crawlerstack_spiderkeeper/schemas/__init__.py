from typing import Dict

from pydantic import BaseModel


class AppData(BaseModel):
    app_id: str
    data: Dict
