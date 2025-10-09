from pathlib import Path
import json
import time
import uuid
from typing import Dict, Any
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from .config import paths

class AuditManager:
    def init_keys(self):
        p = paths().keys
        p.mkdir(parents=True, exist_ok=True)
        priv_path = p / "private.pem"
        pub_path = p / "public.pem"
        if priv_path.exists() and pub_path.exists():
            return
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()
        priv_path.write_bytes(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
        pub_path.write_bytes(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))

    def record(self, event: str, plan: Dict[str, Any], extra: Dict[str, Any] | None = None, actor: str | None = None) -> str:
        self.init_keys()
        audit_id = str(uuid.uuid4())
        data = {
            "id": audit_id,
            "event": event,
            "ts": int(time.time()),
            "plan_id": plan.get("id"),
            "targets": plan.get("targets", []),
            "actor": actor or "unknown",
            "payload": extra or {},
        }
        blob = json.dumps(data, sort_keys=True).encode()
        priv = (paths().keys / "private.pem").read_bytes()
        private_key = serialization.load_pem_private_key(priv, password=None)
        signature = private_key.sign(blob, padding.PKCS1v15(), hashes.SHA256())
        entry = {"data": data, "sig": signature.hex()}
        out = paths().audits / f"{audit_id}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(entry, indent=2))
        return audit_id

    def verify(self, audit_id: str) -> bool:
        p = paths().audits / f"{audit_id}.json"
        if not p.exists():
            return False
        entry = json.loads(p.read_text())
        blob = json.dumps(entry["data"], sort_keys=True).encode()
        sig = bytes.fromhex(entry["sig"])
        pub = (paths().keys / "public.pem").read_bytes()
        public_key = serialization.load_pem_public_key(pub)
        try:
            public_key.verify(sig, blob, padding.PKCS1v15(), hashes.SHA256())
            return True
        except Exception:
            return False
