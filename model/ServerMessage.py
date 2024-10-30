from pydantic import BaseModel
from enum import Enum


class TypeServerMessage(str, Enum):
    RENDER_MAP = "render_map"
    UPDATE_OBJECTS = "update"
    REGISTRATE_ACCEPT = "reg"
    START_GAME = "start"
    VOID = "VOID"
    STOP_GAME = "stop"


class ServerMessage(BaseModel):
    type_message: TypeServerMessage
    body: dict
