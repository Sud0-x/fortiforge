from fortiforge.pipeline.intent_parser import IntentParser
from fortiforge.pipeline.planner import ActionPlanner
from fortiforge.rules_db.search import RulesCatalog
from fortiforge.inventory import Inventory

def test_planner_plan_contains_steps_and_targets():
    parser = IntentParser()
    planner = ActionPlanner(RulesCatalog())
    inv = Inventory.load(None)
    parsed = parser.parse("Harden nginx servers and enable fail2ban")
    plan = planner.build_plan(parsed, inv, label_filter=["web"]) 
    assert plan["steps"], "Expected steps generated from templates"
    assert plan["targets"], "Expected targets resolved from inventory"
