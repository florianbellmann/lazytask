from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class Task:
    id: str
    title: str
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: Optional[int] = None  # e.g., 1 (high) to 5 (low)
    flagged: bool = False
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class TaskList:
    id: str
    name: str
    tasks: List[Task] = field(default_factory=list)
