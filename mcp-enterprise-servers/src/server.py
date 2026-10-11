"""MCP server exposing approved, validated, read-only operations over enterprise data.

The model never receives database credentials or arbitrary SQL execution. It can only call
the tools below, each of which validates its parameters on the server side.
"""
import logging
import re
from typing import Literal
from mcp.server.fastmcp import FastMCP
from .db import connect

logging.basicConfig(filename="audit.log", level=logging.INFO, format="%(asctime)s %(message)s")
mcp = FastMCP("enterprise-operations")
SITE_PATTERN = re.compile(r"^SITE-\d{3}$")


def _audit(tool: str, **params):
    logging.info("tool=%s params=%s", tool, params)


@mcp.tool()
def get_site_status(site_id: str) -> dict:
    """Return the status, region and open incident count for one site (format SITE-123)."""
    _audit("get_site_status", site_id=site_id)
    if not SITE_PATTERN.match(site_id):
        return {"error": "VALIDATION_ERROR", "detail": "site_id must match SITE-123"}
    with connect() as conn:
        row = conn.execute("SELECT * FROM sites WHERE site_id = ?", (site_id,)).fetchone()
    return dict(row) if row else {"error": "NOT_FOUND", "detail": site_id}


@mcp.tool()
def list_sites_by_status(status: Literal["UP", "DOWN", "DEGRADED"], limit: int = 10) -> list[dict]:
    """List sites with the given status. The limit is capped at 50."""
    _audit("list_sites_by_status", status=status, limit=limit)
    limit = max(1, min(limit, 50))
    with connect() as conn:
        rows = conn.execute("SELECT * FROM sites WHERE status = ? LIMIT ?", (status, limit)).fetchall()
    return [dict(r) for r in rows]


@mcp.resource("schema://sites")
def sites_schema() -> str:
    """Readable context: the schema of the sites table."""
    return "sites(site_id TEXT, status TEXT[UP|DOWN|DEGRADED], region TEXT, open_incidents INTEGER)"


if __name__ == "__main__":
    mcp.run()
