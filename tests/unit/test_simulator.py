from fortiforge.pipeline.simulator import Simulator
from fortiforge.pipeline.intent_parser import IntentParser
from fortiforge.pipeline.planner import ActionPlanner
from fortiforge.rules_db.search import RulesCatalog
from fortiforge.inventory import Inventory

def test_simulation_produces_diffs():
    parser = IntentParser()
    planner = ActionPlanner(RulesCatalog())
    inv = Inventory.load(None)
    parsed = parser.parse("Harden nginx and add firewall rules to block SQLi")
    plan = planner.build_plan(parsed, inv, label_filter=["web"]) 
    report = Simulator().simulate(plan)
    assert report["summary"]["changes"] >= 1
