import uuid
from typing import Dict, Any, List
import networkx as nx

from ..rules_db.search import RulesCatalog
from ..inventory import Inventory

class ActionPlanner:
    def __init__(self, catalog: RulesCatalog):
        self.catalog = catalog

    def build_plan(self, parsed: Dict[str, Any], inv: Inventory, label_filter: List[str]) -> Dict[str, Any]:
        targets = [inv.authorized_label(h) for h in inv.resolve_targets(label_filter)]
        # Build dependency graph: firewall before service hardening, hardening before fail2ban
        G = nx.DiGraph()
        action_nodes = []
        for act in parsed.get("actions", []):
            node_id = act["id"]
            G.add_node(node_id, action=act)
            action_nodes.append(node_id)
        # naive dependency ordering
        for a in parsed.get("actions", []):
            if a["kind"] == "service_enable":
                # depend on service_hardening if same service mentioned
                for b in parsed.get("actions", []):
                    if b["kind"] == "service_hardening":
                        G.add_edge(b["id"], a["id"])  # hardening before enabling
            if a["kind"] == "service_hardening":
                for b in parsed.get("actions", []):
                    if b["kind"] == "firewall_rules":
                        G.add_edge(b["id"], a["id"])  # firewall first
        ordered = list(nx.topological_sort(G)) if nx.is_directed_acyclic_graph(G) else action_nodes
        # Expand templates into concrete tasks
        steps: List[Dict[str, Any]] = []
        for node_id in ordered:
            act = G.nodes[node_id]["action"]
            for t in act.get("templates", []):
                tpl = self.catalog.get_by_key(t)
                if not tpl:
                    continue
                steps.append({
                    "action_id": node_id,
                    "kind": act["kind"],
                    "template": t,
                    "template_meta": tpl,
                })
        plan = {
            "id": str(uuid.uuid4()),
            "description": parsed.get("description", ""),
            "targets": targets,
            "ordered_actions": ordered,
            "steps": steps,
        }
        return plan
