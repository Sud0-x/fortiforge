from pathlib import Path
from typing import List, Dict, Any
import json
import shutil
import fnmatch

from ..config import paths

class RulesCatalog:
    def __init__(self):
        self.root = paths().rules_root

    def iter_items(self) -> List[Dict[str, Any]]:
        items = []
        for p in self.root.rglob("*.yml"):
            items.append(self._load_item(p))
        for p in self.root.rglob("*.yaml"):
            items.append(self._load_item(p))
        for p in self.root.rglob("*.json"):
            items.append(self._load_item(p))
        return [i for i in items if i]

    def _load_item(self, path: Path) -> Dict[str, Any] | None:
        import yaml
        try:
            data = yaml.safe_load(path.read_text())
            data["path"] = str(path)
            return data
        except Exception:
            return None

    def search(self, q: str, tags: List[str] | None = None) -> List[Dict[str, Any]]:
        ql = q.lower()
        res = []
        for item in self.iter_items():
            name = str(item.get("name", "")).lower()
            kind = str(item.get("kind", "")).lower()
            content = str(item.get("content", "")).lower()
            itags = [t.lower() for t in item.get("tags", [])]
            if ql in name or ql in content or ql in kind:
                if tags:
                    if not set([t.lower() for t in tags]).issubset(set(itags)):
                        continue
                res.append(item)
        return res

    def get_by_key(self, key: str) -> Dict[str, Any] | None:
        # key is expected to map to `key` field or file stem
        for item in self.iter_items():
            if item.get("key") == key:
                return item
        return None

    def import_pack(self, pack_path: Path) -> List[Path]:
        dests = []
        dest_root = self.root / "custom"
        dest_root.mkdir(parents=True, exist_ok=True)
        for p in pack_path.rglob("*"):
            if p.is_file() and any(p.name.endswith(ext) for ext in [".yml", ".yaml", ".json"]):
                rel = p.relative_to(pack_path)
                dest = dest_root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dest)
                dests.append(dest)
        return dests
