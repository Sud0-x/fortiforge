import difflib
from typing import Dict, Any

class Simulator:
    def simulate(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        # Produce a simple diff preview per step; we do not access real hosts in simulation
        report = {
            "plan_id": plan.get("id"),
            "targets": plan.get("targets", []),
            "steps": [],
            "summary": {"changes": 0},
        }
        changes = 0
        for step in plan.get("steps", []):
            desired = step.get("template_meta", {}).get("content", "")
            current = ""  # unknown; simulate as empty baseline
            diff = list(difflib.unified_diff(
                current.splitlines(keepends=True),
                desired.splitlines(keepends=True),
                fromfile="current",
                tofile=step.get("template", "desired"),
            ))
            report["steps"].append({
                "template": step.get("template"),
                "kind": step.get("kind"),
                "diff": "".join(diff),
                "risk": step.get("template_meta", {}).get("risk", "low"),
            })
            if diff:
                changes += 1
        report["summary"]["changes"] = changes
        return report
