from src.classifier import train
from src.ner import extract_entities, priority
from src.triage import triage

model, meta = train()


def test_macro_f1():
    assert meta["macro_f1"] >= 0.85


def test_classification_examples():
    assert triage("refund for invoice INV-12345 not processed", model)["category"] == "Billing"
    assert triage("VPN tunnel keeps dropping", model)["category"] == "Network"


def test_entities():
    labels = {e["label"]: e["text"] for e in extract_entities(
        "Ticket INC123456: SAP error E401 from 10.1.2.3, mail a.b@example.com")}
    assert labels == {"TICKET_ID": "INC123456", "PRODUCT": "SAP", "ERROR_CODE": "E401",
                      "IP_ADDRESS": "10.1.2.3", "EMAIL": "a.b@example.com"}


def test_priority():
    assert priority("ASAP please, production is down").startswith("P1")
    assert priority("printer paper jam").startswith("P3")
