from pathlib import Path
from typing import List, Dict
from .rules_db.search import RulesCatalog

class Recommender:
    def __init__(self):
        self.catalog = RulesCatalog()

    def suggest(self, labels: List[str]) -> List[Dict]:
        suggestions = []
        labs = [l.lower() for l in labels]
        if any("ubuntu" in l for l in labs):
            suggestions += self.catalog.search("ubuntu", tags=["hardening"])  # os hardening
        if any("web" in l for l in labs) or any("nginx" in l for l in labs):
            suggestions += self.catalog.search("nginx", tags=["hardening"])  # nginx templates
        if any("cloud" in l for l in labs) and any("aws" in l for l in labs):
            suggestions += self.catalog.search("aws", tags=["sg"])  # AWS SG
        return suggestions[:10]
