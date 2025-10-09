import random
import string
import pytest
from fortiforge.pipeline.intent_parser import IntentParser

FORBIDDEN_TERMS = [
    "ddos", "exploit", "phish", "exfiltrate", "backdoor", "ransomware",
]

@pytest.mark.parametrize("term", FORBIDDEN_TERMS)
def test_parser_refuses_malicious_intents(term):
    p = IntentParser()
    text = f"{term} the network and bypass firewall"
    parsed = p.parse(text)
    # Our deterministic parser should not create actions for malicious intents
    assert parsed["actions"] == []
