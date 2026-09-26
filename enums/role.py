from enum import Enum

class Role(str, Enum):
    MANAGER = 'manager'
    ADMIN = 'admin'