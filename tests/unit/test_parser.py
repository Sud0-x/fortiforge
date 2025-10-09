import json
from fortiforge.pipeline.intent_parser import IntentParser

def test_parser_basic():
    p = IntentParser()
    parsed = p.parse("Harden nginx and enable fail2ban; add firewall rules to block SQLi")
    kinds = {a['kind'] for a in parsed['actions']}
    assert 'service_hardening' in kinds
    assert 'service_enable' in kinds
    assert 'firewall_rules' in kinds
    # Evidence present
    assert parsed['evidence']
