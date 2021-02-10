from pydantic import BaseModel, constr

from crawlerstack_spiderkeeper.schemas.base import InDBMixin


class ServerBase(BaseModel):
    name: str
    type: str
    uri: str
    enable: bool = False


class Server(ServerBase, InDBMixin):
    pass


class ServerCreate(ServerBase):
    name: constr(max_length=45)
    type: constr(max_length=45)
    uri: constr(max_length=100)


class ServerUpdate(ServerBase):
    name: constr(max_length=45) = None
    type: constr(max_length=45) = None
    uri: constr(max_length=100) = None
    enable: bool = None
