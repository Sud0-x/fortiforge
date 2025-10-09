from dataclasses import dataclass, field
from typing import List, Dict, Any
import uuid

@dataclass
class Action:
    id: str
    kind: str
    description: str
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Plan:
    id: str
    description: str
    actions: List[Action]
    targets: List[str]
