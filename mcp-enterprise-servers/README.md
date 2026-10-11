# MCP Enterprise Servers

![Python 3.10+](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white) ![MCP](https://img.shields.io/badge/MCP-000000?style=flat-square&logo=anthropic&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) ![License MIT](https://img.shields.io/badge/License_MIT-FF3B3B?style=flat-square&logo=opensourceinitiative&logoColor=white) [![CI](https://github.com/raj75114043-design/ai-ml-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/raj75114043-design/ai-ml-portfolio/actions/workflows/ci.yml) [![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://raj-mcp-enterprise-servers.streamlit.app) [![Docker](https://img.shields.io/badge/Docker-ghcr.io-2496ED?style=flat-square&logo=docker&logoColor=white)](https://github.com/users/raj75114043-design/packages/container/package/mcp-enterprise-servers)

A reference **Model Context Protocol** server that exposes enterprise operational data to AI agents
through approved, validated and audited tools — instead of giving the model direct database access.

## Why MCP

- An integration exposed once through an MCP server can be used by any compatible AI client
- Authentication, authorisation and business rules remain on the server side
- The model receives no credentials and cannot execute arbitrary queries

## Tools and Resources

| Type | Name | Purpose |
|---|---|---|
| Tool | `get_site_status(site_id)` | Status, region and incident count for one site |
| Tool | `list_sites_by_status(status, limit)` | Filtered list with an enforced limit |
| Resource | `schema://sites` | Table schema as readable context |

## Security Controls

| Control | Implementation |
|---|---|
| Least privilege | SQLite connection opened in read-only mode |
| Input validation | Regex and `Literal` types validated server-side |
| Injection safety | Parameterised queries only |
| Auditability | Every tool call written to `audit.log` |
| Structured errors | `VALIDATION_ERROR` / `NOT_FOUND` so agents can self-correct |

## Quick Start

```bash
pip install -r requirements.txt
python test_tools.py          # direct verification
python -m src.server          # run as an MCP server (stdio)
```

### Connect to an MCP client

```json
{
  "mcpServers": {
    "enterprise-operations": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/mcp-enterprise-servers"
    }
  }
}
```

> All data in this repository is synthetic.

## Web Application

A Streamlit tool explorer that calls the same MCP tools an agent would, shows the structured responses and validation errors, and displays the live audit log.

## Run, Deploy and Test

**Web application**

```bash
cd mcp-enterprise-servers
pip install -r requirements.txt
streamlit run app.py
```

Live demo: https://raj-mcp-enterprise-servers.streamlit.app

**Docker**

```bash
docker build -t mcp-enterprise-servers .
docker run -p 8501:8501 mcp-enterprise-servers
# or pull the published image
docker pull ghcr.io/raj75114043-design/mcp-enterprise-servers:latest
```

**Tests**

```bash
pytest -q
```

Every push to the [`ai-ml-portfolio`](https://github.com/raj75114043-design/ai-ml-portfolio) repository runs this project's tests through GitHub Actions and publishes its Docker image to GitHub Container Registry.
