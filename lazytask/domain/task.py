from dataclasses import dataclass, field
from typing import Optional, List
import datetime

@dataclass
class Task:
    id: str
    title: str
    completed: bool = False
    due_date: Optional[datetime.date] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: Optional[int] = None
    is_flagged: bool = False
    recurring: Optional[str] = None