"""Rule-based entity extraction for IDs and codes that must be captured exactly."""
import re

PRODUCTS = ["Outlook", "SAP", "VPN client", "Teams", "billing portal", "Salesforce", "Wi-Fi", "Jira", "Excel"]
PATTERNS = {
    "TICKET_ID": r"\bINC\d{6}\b",
    "INVOICE": r"\bINV-\d{5}\b",
    "ACCOUNT": r"\bAC\d{6}\b",
    "ERROR_CODE": r"\bE\d{3}\b",
    "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "EMAIL": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
    "PRODUCT": r"\b(?:" + "|".join(re.escape(p) for p in PRODUCTS) + r")\b",
}
URGENT = re.compile(r"\b(urgent|asap|production is down|blocking|critical)\b", re.I)


def extract_entities(text: str) -> list[dict]:
    found = []
    for label, pattern in PATTERNS.items():
        for m in re.finditer(pattern, text, flags=re.I if label == "PRODUCT" else 0):
            found.append({"text": m.group(0), "label": label, "start": m.start(), "end": m.end()})
    found.sort(key=lambda e: e["start"])
    return found


def priority(text: str) -> str:
    return "P1 - High" if URGENT.search(text) else "P3 - Normal"
