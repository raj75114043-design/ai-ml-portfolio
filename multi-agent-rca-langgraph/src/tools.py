"""Read-only tools over the sample network data. In production these sit behind MCP servers."""
import json
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parent.parent / "data" / "network.json").read_text())


def get_site(site_id: str) -> dict:
    if site_id not in DATA["sites"]:
        raise ValueError(f"Unknown site: {site_id}")
    return {"site_id": site_id, **DATA["sites"][site_id]}


def get_activity(activity_id: str) -> dict:
    return {"activity_id": activity_id, **DATA["activities"][activity_id]}


def get_material(material_id: str) -> dict:
    return {"material_id": material_id, **DATA["materials"][material_id]}


def get_vendor(vendor_id: str) -> dict:
    return {"vendor_id": vendor_id, **DATA["vendors"][vendor_id]}
