import json
from flask import Flask, jsonify, request, render_template
from ..config import paths
from ..rules_db.search import RulesCatalog
from ..audit import AuditManager
from ..rbac import init_db, authenticate, verify_token, create_user

def create_app() -> Flask:
    app = Flask(__name__, template_folder="../ui/templates", static_folder="../ui/static")
    init_db()

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/auth/login")
    def api_login():
        data = request.get_json(force=True) or {}
        token = authenticate(data.get("username",""), data.get("password",""))
        if not token:
            return jsonify({"error":"invalid_credentials"}), 401
        return jsonify({"token": token})

    @app.post("/api/auth/bootstrap")
    def api_bootstrap_user():
        # Create a default admin if needed (only on localhost for demo)
        data = request.get_json(force=True) or {}
        try:
            username = data.get("username","admin")
            password = data.get("password","admin")
            role = data.get("role","admin")
            create_user(username, password, role)
            return jsonify({"ok": True, "user": username, "role": role})
        except Exception as e:
            # If user already exists, that's ok for bootstrap
            if "UNIQUE constraint" in str(e) or "already exists" in str(e).lower():
                return jsonify({"ok": True, "message": "User already exists"})
            return jsonify({"error": str(e)}), 400

    def require_role(req, roles):
        auth = req.headers.get("Authorization","")
        if not auth.startswith("Bearer "):
            return None
        token = auth.split(" ",1)[1]
        claims = verify_token(token)
        if not claims or claims.get("role") not in roles:
            return None
        return claims

    @app.get("/api/rules/search")
    def api_rules_search():
        q = request.args.get("q", "")
        tags = request.args.get("tags", "")
        rc = RulesCatalog()
        res = rc.search(q, tags=[t.strip() for t in tags.split(",") if t.strip()])
        return jsonify(res)

    @app.get("/api/audit/<audit_id>/verify")
    def api_verify_audit(audit_id):
        claims = require_role(request, roles={"admin","auditor"})
        if not claims:
            return jsonify({"error":"unauthorized"}), 403
        ok = AuditManager().verify(audit_id)
        return jsonify({"ok": bool(ok)})

    @app.post("/api/plans/<plan_id>/apply")
    def api_apply(plan_id):
        claims = require_role(request, roles={"admin","operator"})
        if not claims:
            return jsonify({"error":"unauthorized"}), 403
        data = request.get_json(force=True) or {}
        consent = data.get("consent","")
        if consent != "I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY":
            return jsonify({"error":"consent_required"}), 400
        plan_path = paths().plans / f"{plan_id}.json"
        if not plan_path.exists():
            return jsonify({"error":"plan_not_found"}), 404
        plan = json.loads(plan_path.read_text())
        audit_id = AuditManager().record(event="api_apply_requested", plan=plan, extra={"sandbox": True}, actor=f"api:{claims.get('sub')}")
        return jsonify({"ok": True, "audit_id": audit_id})

    @app.post("/api/plans/<plan_id>/rollback")
    def api_rollback(plan_id):
        claims = require_role(request, roles={"admin"})
        if not claims:
            return jsonify({"error":"unauthorized"}), 403
        plan_path = paths().plans / f"{plan_id}.json"
        if not plan_path.exists():
            return jsonify({"error":"plan_not_found"}), 404
        plan = json.loads(plan_path.read_text())
        audit_id = AuditManager().record(event="api_rollback_requested", plan=plan, actor=f"api:{claims.get('sub')}")
        return jsonify({"ok": True, "audit_id": audit_id})

    return app
