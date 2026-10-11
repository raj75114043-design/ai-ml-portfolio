import csv
from pathlib import Path
import networkx as nx
from .entity_resolution import resolve
from .ontology import RELATIONSHIPS

DATA = Path(__file__).resolve().parent.parent / "data"


def read(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build():
    g = nx.MultiDiGraph()
    review = []
    vendors = {r["vendor_id"]: r["vendor_name"] for r in read("vendors.csv")}
    for vid, vname in vendors.items():
        g.add_node(vid, label="Vendor", name=vname)
    for m in read("materials.csv"):
        g.add_node(m["material_id"], label="Material", name=m["material_name"])
        vid, score = resolve(m["vendor_name"], vendors)
        if vid:
            g.add_edge(m["material_id"], vid, type="SUPPLIED_BY", confidence=score,
                       source_name=m["vendor_name"])
        else:
            review.append((m["material_id"], m["vendor_name"], score))
    for a in read("activities.csv"):
        g.add_node(a["site_id"], label="Site", name=a["site_id"])
        g.add_node(a["activity_id"], label="Activity", name=a["activity_name"], status=a["status"])
        g.add_edge(a["site_id"], a["activity_id"], type="HAS_ACTIVITY")
        g.add_edge(a["activity_id"], a["material_id"], type="USES_MATERIAL")
    validate(g)
    return g, review


def validate(g):
    for u, v, d in g.edges(data=True):
        triple = (g.nodes[u]["label"], d["type"], g.nodes[v]["label"])
        assert triple in RELATIONSHIPS, f"Schema violation: {triple}"


def to_cypher(g) -> list[str]:
    """Idempotent MERGE statements for loading into Neo4j."""
    stmts = [f"MERGE (n:{d['label']} {{id: '{n}'}}) SET n.name = '{d['name']}'" for n, d in g.nodes(data=True)]
    for u, v, d in g.edges(data=True):
        stmts.append(f"MATCH (a {{id: '{u}'}}), (b {{id: '{v}'}}) MERGE (a)-[:{d['type']}]->(b)")
    return stmts
