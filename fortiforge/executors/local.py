from pathlib import Path
from typing import Dict, Any, List
import time
import threading

class LocalSandboxExecutor:
    """
    Executes tasks in docker containers defined by sandbox/docker-compose.yml.
    Default mode is simulate-only unless explicit consent and env allow non-sandbox.
    """
    def __init__(self, concurrency: int = 2, rate_limit: int = 2, timeout: int = 60):
        self.concurrency = concurrency
        self.rate_limit = rate_limit
        self.timeout = timeout

    def execute(self, playbook: Dict[str, Any]) -> Dict[str, Any]:
        # For demo, we do not execute commands; we simulate application in containers.
        results = {"ok": True, "applied": 0, "details": []}
        last = 0.0
        for t in playbook.get("tasks", []):
            now = time.time()
            if now - last < 1.0 / max(1, self.rate_limit):
                time.sleep((1.0 / max(1, self.rate_limit)) - (now - last))
            last = time.time()
            results["details"].append({"task": t.get("name"), "status": "simulated"})
            results["applied"] += 1
        return results
