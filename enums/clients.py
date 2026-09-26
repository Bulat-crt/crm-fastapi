from enum import Enum

class ClientSort(str, Enum):
    NAME = 'name'
    CREATED_AT = 'created_at'