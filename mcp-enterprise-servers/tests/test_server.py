from src.db import init
from src.server import get_site_status, list_sites_by_status

init()


def test_valid_site():
    assert get_site_status("SITE-101")["status"] == "DOWN"


def test_injection_rejected():
    assert get_site_status("SITE-101; DROP TABLE sites")["error"] == "VALIDATION_ERROR"


def test_not_found():
    assert get_site_status("SITE-999")["error"] == "NOT_FOUND"


def test_list_and_limit():
    rows = list_sites_by_status("UP", 1000)
    assert rows and all(r["status"] == "UP" for r in rows)
