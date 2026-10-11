from src.builder import build, to_cypher, validate
from src.entity_resolution import resolve

g, review = build()


def test_schema_valid():
    validate(g)


def test_entity_resolution_handles_variants():
    master = {"VEN-B": "Beta Power Systems", "VEN-A": "Alpha Infra Supplies Pvt Ltd"}
    assert resolve("BETA POWER SYSTEMS LTD", master)[0] == "VEN-B"
    assert resolve("Alpha Infra Suppliers", master)[0] == "VEN-A"


def test_unrelated_name_goes_to_review():
    assert resolve("Zeta Logistics", {"VEN-B": "Beta Power Systems"})[0] is None


def test_multi_hop_reaches_vendor():
    vendors = {v for a in g.successors("SITE-101") for m in g.successors(a) for v in g.successors(m)}
    assert "VEN-A" in vendors


def test_cypher_is_idempotent():
    assert all("MERGE" in s for s in to_cypher(g))
