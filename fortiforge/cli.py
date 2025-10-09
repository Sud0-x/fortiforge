import json
import os
import sys
import uuid
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import get_home, paths
from .pipeline.intent_parser import IntentParser
from .pipeline.planner import ActionPlanner
from .pipeline.simulator import Simulator
from .playbooks.generator import PlaybookGenerator
from .inventory import Inventory
from .rules_db.search import RulesCatalog
from .audit import AuditManager

console = Console()

@click.group()
@click.version_option(__version__, prog_name="fortiforge")
def cli():
    """FortiForge CLI (defensive-only). Developer: Sud0-x"""

@cli.group(invoke_without_command=True)
@click.argument("instruction", nargs=-1, required=False)
@click.option("--inventory", "inventory_path", type=click.Path(exists=False), default=None)
@click.option("--labels", help="Comma-separated labels to scope targets (e.g., web,prod)", default="")
def plan(instruction, inventory_path, labels):
    """Plan operations. Use `fortiforge plan "<nl-text>"` to create quickly, or subcommands."""
    if instruction:
        # fast path: `fortiforge plan "..."`
        text = " ".join(instruction)
        inv = Inventory.load(inventory_path)
        parser = IntentParser()
        planner = ActionPlanner(RulesCatalog())
        parsed = parser.parse(text)
        plan = planner.build_plan(parsed, inv, label_filter=[l.strip() for l in labels.split(",") if l.strip()])
        plan_id = plan["id"]
        plan_file = paths().plans / f"{plan_id}.json"
        plan_file.parent.mkdir(parents=True, exist_ok=True)
        plan_file.write_text(json.dumps(plan, indent=2))
        console.print(f"Plan created. Plan ID: {plan_id}")

@plan.command("create")
@click.argument("instruction", nargs=-1, required=True)
@click.option("--inventory", "inventory_path", type=click.Path(exists=False), default=None)
@click.option("--labels", help="Comma-separated labels to scope targets (e.g., web,prod)", default="")
def plan_create(instruction, inventory_path, labels):
    text = " ".join(instruction)
    inv = Inventory.load(inventory_path)
    parser = IntentParser()
    planner = ActionPlanner(RulesCatalog())
    parsed = parser.parse(text)
    plan = planner.build_plan(parsed, inv, label_filter=[l.strip() for l in labels.split(",") if l.strip()])
    plan_id = plan["id"]
    plan_file = paths().plans / f"{plan_id}.json"
    plan_file.parent.mkdir(parents=True, exist_ok=True)
    plan_file.write_text(json.dumps(plan, indent=2))
    console.print(f"Plan created. Plan ID: {plan_id}")

@plan.command("list")
def plan_list():
    p = paths().plans
    p.mkdir(parents=True, exist_ok=True)
    table = Table(title="Plans")
    table.add_column("ID")
    table.add_column("Description")
    table.add_column("Targets")
    for f in sorted(p.glob("*.json")):
        data = json.loads(f.read_text())
        table.add_row(data.get("id","-"), data.get("description",""), ",".join(data.get("targets", [])))
    console.print(table)

@plan.command("show")
@click.argument("plan_id")
def plan_show(plan_id):
    plan_path = paths().plans / f"{plan_id}.json"
    if not plan_path.exists():
        raise click.ClickException("Plan not found")
    console.print_json(plan_path.read_text())

@cli.command()
@click.argument("plan_id")
@click.option("--report", type=click.Path(), default=None)
def simulate(plan_id, report):
    plan_path = paths().plans / f"{plan_id}.json"
    if not plan_path.exists():
        raise click.ClickException("Plan not found")
    sim = Simulator()
    report_data = sim.simulate(json.loads(plan_path.read_text()))
    if report:
        Path(report).parent.mkdir(parents=True, exist_ok=True)
        Path(report).write_text(json.dumps(report_data, indent=2))
        console.print(f"Simulation report written to {report}")
    else:
        console.print_json(data=report_data)

@cli.command()
@click.argument("plan_id")
@click.option("--consent", required=True, help="Must be exactly: I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY")
@click.option("--sandbox", is_flag=True, help="Restrict to sandbox targets (docker compose)")
@click.option("--concurrency", default=2, show_default=True)
@click.option("--rate-limit", default=2, show_default=True, help="ops per second")
@click.option("--timeout", default=60, show_default=True)
def apply(plan_id, consent, sandbox, concurrency, rate_limit, timeout):
    if consent != "I_AUTHORIZE_CHANGES_ON_THIS_INVENTORY":
        raise click.ClickException("Consent phrase mismatch.")
    non_sandbox_allowed = os.environ.get("FORTIFORGE_ALLOW_NON_SANDBOX") == "1"
    plan_path = paths().plans / f"{plan_id}.json"
    if not plan_path.exists():
        raise click.ClickException("Plan not found")
    plan = json.loads(plan_path.read_text())
    # Enforce authorization at target level
    unauthorized = [t for t in plan.get("targets", []) if not t.endswith(":authorized")]
    if unauthorized:
        raise click.ClickException("Plan contains unauthorized targets. Use inventory to authorize explicitly.")
    if not sandbox and not non_sandbox_allowed:
        raise click.ClickException("Non-sandbox apply is disabled by default. Set FORTIFORGE_ALLOW_NON_SANDBOX=1 to allow.")
    # Generate playbook and execute
    generator = PlaybookGenerator()
    playbook = generator.generate_from_plan(plan)
    # Write playbook for audit
    pb_path = paths().playbooks / f"{plan_id}.yaml"
    pb_path.parent.mkdir(parents=True, exist_ok=True)
    pb_path.write_text(playbook)
    # Audit record
    audit = AuditManager()
    actor = f"cli:{os.getenv('USER','unknown')}"
    audit_id = audit.record(event="apply_requested", plan=plan, extra={"sandbox": sandbox}, actor=actor)
    console.print(f"Apply requested (audit id: {audit_id}). For demo, actual execution is simulated.")
    console.print("To execute in sandbox, run: docker compose -f sandbox/docker-compose.yml up -d --build")

@cli.command()
@click.argument("plan_id")
@click.option("--confirm", is_flag=True, required=True)
def rollback(plan_id, confirm):
    if not confirm:
        raise click.ClickException("--confirm required")
    plan_path = paths().plans / f"{plan_id}.json"
    if not plan_path.exists():
        raise click.ClickException("Plan not found")
    audit = AuditManager()
    audit_id = audit.record(event="rollback_requested", plan=json.loads(plan_path.read_text()))
    console.print(f"Rollback requested (audit id {audit_id}). This demo does not perform live rollbacks.")

@cli.group()
def inventory():
    """Manage inventory files."""

@inventory.command("list")
@click.option("--path", "inventory_path", type=click.Path(exists=False), default=None)
def inventory_list(inventory_path):
    inv = Inventory.load(inventory_path)
    table = Table(title="Inventory Hosts")
    table.add_column("Name")
    table.add_column("Conn")
    table.add_column("Labels")
    table.add_column("Authorized")
    for h in inv.hosts:
        table.add_row(h["name"], h.get("connection","-"), ",".join(h.get("labels",[])), str(h.get("authorized", False)))
    console.print(table)

@inventory.command("add")
@click.option("--file", "file", type=click.Path(exists=True), required=True)
def inventory_add(file):
    dest = get_home() / "inventory" / Path(file).name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(Path(file).read_text())
    console.print(f"Inventory added at {dest}")

@cli.group()
def rules():
    """Search and import/export rules database."""

@rules.command("search")
@click.option("--q", required=True, help="query string")
@click.option("--tags", default="")
def rules_search(q, tags):
    catalog = RulesCatalog()
    results = catalog.search(q, tags=[t.strip() for t in tags.split(",") if t.strip()])
    table = Table(title="Rules Search Results")
    table.add_column("Kind")
    table.add_column("Name")
    table.add_column("Path")
    table.add_column("Tags")
    for r in results:
        table.add_row(r.get("kind","-"), r.get("name","-"), r.get("path","-"), ",".join(r.get("tags", [])))
    console.print(table)

@rules.command("import")
@click.argument("pack_path", type=click.Path(exists=True))
def rules_import(pack_path):
    catalog = RulesCatalog()
    dest_paths = catalog.import_pack(Path(pack_path))
    console.print(f"Imported {len(dest_paths)} files.")

@rules.command("export")
@click.option("--q", required=True, help="query to match for export")
@click.option("--out", required=True, type=click.Path())
def rules_export(q, out):
    from shutil import copy2
    outp = Path(out)
    outp.mkdir(parents=True, exist_ok=True)
    catalog = RulesCatalog()
    items = catalog.search(q)
    for it in items:
        src = Path(it["path"]) if it.get("path") else None
        if src and src.exists():
            copy2(src, outp / src.name)
    console.print(f"Exported {len(items)} items to {outp}")

@cli.group()
def playbook():
    """Create or list playbooks."""

@playbook.command("list")
def playbook_list():
    p = paths().playbooks
    p.mkdir(parents=True, exist_ok=True)
    for f in sorted(p.glob("*.yaml")):
        console.print(f"- {f}")

@playbook.command("create")
@click.option("--name", required=True)
@click.option("--templates", help="Comma-separated template keys", required=True)
@click.option("--targets", help="Comma-separated targets", required=False, default="")
def playbook_create(name, templates, targets):
    from .rules_db.search import RulesCatalog
    import yaml
    catalog = RulesCatalog()
    tks = [t.strip() for t in templates.split(",") if t.strip()]
    items = [catalog.get_by_key(k) for k in tks]
    items = [i for i in items if i]
    pb = {
        "name": name,
        "targets": [t.strip() for t in targets.split(",") if t.strip()],
        "tasks": [
            {
                "name": f"Apply template {i.get('key')}",
                "idempotent": True,
                "simulate": {"show_diff": True},
                "apply": {"mode":"template", "content": i.get("content", "")},
                "rollback": i.get("rollback", {}),
            } for i in items
        ]
    }
    out = paths().playbooks / f"{name}.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(pb, sort_keys=False))
    console.print(f"Playbook created at {out}")

@cli.group()
def audit():
    """Audit utilities."""

@audit.command("init-keys")
def audit_init_keys():
    AuditManager().init_keys()
    console.print("Audit keys initialized.")

@audit.command("verify-audit")
@click.argument("audit_id")
def verify_audit(audit_id):
    ok = AuditManager().verify(audit_id)
    if ok:
        console.print("Audit entry verified.")
    else:
        console.print("Audit verification failed.")

@cli.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8080, type=int)
def serve(host, port):
    from .api.server import create_app
    app = create_app()
    app.run(host=host, port=port)

if __name__ == "__main__":
    cli()
