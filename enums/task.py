from enum import Enum

class TaskSort(str, Enum):
    DEADLINE = "deadline"
    CREATED_AT = "created_at"
    TITLE = "title"