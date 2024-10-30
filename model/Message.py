from pydantic import BaseModel
from enum import Enum


class TypeMessage(str, Enum):
    MOVE_TANK = "move"
    FIRE = "fire"
    REGISTRATION_PLAYER = "registration"


class BaseMessage(BaseModel):
    uuid: str | None = None
    type_message: TypeMessage
    body: dict | None = None
