"""Calls the tool functions directly to verify validation and data access."""
from src.db import init
from src.server import get_site_status, list_sites_by_status

init()
print(get_site_status("SITE-101"))
print(get_site_status("SITE-101; DROP TABLE sites"))
print(list_sites_by_status("UP"))
