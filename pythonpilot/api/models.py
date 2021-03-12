from dataclasses import dataclass
from enum import Enum
from typing import List


class Permission(Enum):
    U = "u"
    RW = "rw"
    r = "e"


class ObjectType(Enum):
    camera = "kObjectType_Camera"


@dataclass
class Property:
    value: str
    permissions: Permission
    name: str
    prop_id: str
    possible_values: List[str]
