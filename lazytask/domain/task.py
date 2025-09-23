from dataclasses import dataclass, field
from typing import Optional, List
import datetime


@dataclass
class Task:
    id: str
    title: str
    completed: bool = False
    due_date: Optional[datetime.date] = None
    creation_date: Optional[datetime.datetime] = None
    list_name: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: Optional[int] = None
    is_flagged: bool = False
    recurring: Optional[str] = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return self.id == other.id
