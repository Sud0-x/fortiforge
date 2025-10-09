from pathlib import Path
import json
import hashlib
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

class Inventory:
    def __init__(self, hosts: List[Dict[str, Any]], groups: List[Dict[str, Any]]):
        self.hosts = hosts
        self.groups = groups

    @staticmethod
    def load(path: Optional[str] = None) -> "Inventory":
        # Try user home first, otherwise built-in example
        import yaml
        default_path = Path.home() / ".fortiforge" / "inventory" / "sandbox.yaml"
        if path:
            p = Path(path)
            if not p.exists():
                raise FileNotFoundError(f"Inventory not found at {path}")
        elif default_path.exists():
            p = default_path
        else:
            p = Path(__file__).resolve().parent.parent / "inventory" / "examples" / "sandbox.yaml"
        data = yaml.safe_load(p.read_text())
        return Inventory(hosts=data.get("hosts", []), groups=data.get("groups", []))

    def resolve_targets(self, label_filter: List[str]) -> List[Dict[str, Any]]:
        if not label_filter:
            return self.hosts
        lf = set(label_filter)
        return [h for h in self.hosts if lf.intersection(set(h.get("labels", [])))]

    def authorized_label(self, host: Dict[str, Any]) -> str:
        suffix = ":authorized" if host.get("authorized", False) else ""
        return f"{host['name']}{suffix}"
