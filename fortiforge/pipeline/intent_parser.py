import re
import uuid
from typing import Dict, Any, List

try:
    import spacy  # optional
    _NLP = spacy.load("en_core_web_sm")
except Exception:
    _NLP = None

class IntentParser:
    """
    Deterministic, defensive intent parser. Does not execute actions.
    Maps natural-language text to discrete actions with explainable evidence.
    """
    def parse(self, text: str) -> Dict[str, Any]:
        sentences = [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]
        actions: List[Dict[str, Any]] = []
        evidences: List[Dict[str, Any]] = []
        for s in sentences:
            s_lower = s.lower()
            if "harden" in s_lower and ("nginx" in s_lower or "apache" in s_lower):
                svc = "nginx" if "nginx" in s_lower else "apache"
                actions.append({
                    "id": str(uuid.uuid4()),
                    "kind": "service_hardening",
                    "service": svc,
                    "templates": [f"{svc}_baseline_hardening", f"{svc}_tls_hsts"],
                    "description": f"Harden {svc} using baseline and TLS/HSTS",
                })
                evidences.append({"sentence": s, "match": "harden service", "service": svc})
            if "firewall" in s_lower or "block" in s_lower:
                if "sqli" in s_lower or "sql injection" in s_lower:
                    actions.append({
                        "id": str(uuid.uuid4()),
                        "kind": "firewall_rules",
                        "engine": "iptables",
                        "templates": ["fw_block_sqli_patterns", "fw_allow_established", "fw_allow_http_https"],
                        "description": "Add firewall rules to block SQLi patterns and allow web traffic",
                    })
                    evidences.append({"sentence": s, "match": "firewall block sqli"})
            if "fail2ban" in s_lower or ("intrusion" in s_lower and "ban" in s_lower):
                actions.append({
                    "id": str(uuid.uuid4()),
                    "kind": "service_enable",
                    "service": "fail2ban",
                    "templates": ["fail2ban_nginx", "fail2ban_sshd"],
                    "description": "Enable and configure fail2ban for nginx and sshd",
                })
                evidences.append({"sentence": s, "match": "enable fail2ban"})
        # NLP assist (optional, never trusted for execution)
        if _NLP is not None:
            doc = _NLP(text)
            # Extract entities for labels (e.g., prod, kubernetes)
            labels = sorted({ent.text.lower() for ent in doc.ents if ent.label_ in {"ORG", "GPE", "PRODUCT"}})
        else:
            labels = []
        return {
            "id": str(uuid.uuid4()),
            "description": text,
            "actions": actions,
            "evidence": evidences,
            "labels": labels,
        }
