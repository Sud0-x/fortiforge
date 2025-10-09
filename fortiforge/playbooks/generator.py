import yaml
from typing import Dict, Any

class PlaybookGenerator:
    def generate_from_plan(self, plan: Dict[str, Any]) -> str:
        tasks = []
        for step in plan.get("steps", []):
            tasks.append({
                "name": f"Apply template {step.get('template')}",
                "kind": step.get("kind"),
                "idempotent": True,
                "simulate": {"show_diff": True},
                "apply": {"mode": "template", "content": step.get("template_meta", {}).get("content", "")},
                "rollback": step.get("template_meta", {}).get("rollback", {}),
            })
        pb = {
            "name": f"Plan {plan.get('id')}",
            "targets": plan.get("targets", []),
            "tasks": tasks,
        }
        return yaml.safe_dump(pb, sort_keys=False)
