from src.graph import build_graph

app = build_graph()


def ask(q):
    return app.invoke({"query": q})["answer"]


def test_root_cause_identifies_vendor():
    a = ask("Why is SITE-101 down?")
    assert "Steel tower kit" in a and "Alpha Infra Supplies" in a


def test_status_query():
    assert "UP" in ask("What is the status of SITE-102?")


def test_unknown_site_is_handled():
    assert "not found" in ask("Why is SITE-999 down?")


def test_missing_site_id():
    assert "specify a site" in ask("Why is the network slow?")
