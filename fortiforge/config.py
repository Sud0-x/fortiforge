from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class Paths:
    home: Path
    plans: Path
    playbooks: Path
    audits: Path
    keys: Path
    rules_root: Path


def get_home() -> Path:
    base = os.environ.get("FORTIFORGE_HOME", str(Path.home() / ".fortiforge"))
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p


def paths() -> Paths:
    h = get_home()
    return Paths(
        home=h,
        plans=h / "plans",
        playbooks=h / "playbooks",
        audits=h / "audits",
        keys=h / "keys",
        rules_root=Path(__file__).resolve().parent / "rules_db" / "data",
    )
