# Knowledge Graph Builder

![Python 3.10+](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white) ![Neo4j](https://img.shields.io/badge/Neo4j-4581C3?style=flat-square&logo=neo4j&logoColor=white) ![NetworkX](https://img.shields.io/badge/NetworkX-2C3E50?style=flat-square&logo=python&logoColor=white) ![License MIT](https://img.shields.io/badge/License_MIT-FF3B3B?style=flat-square&logo=opensourceinitiative&logoColor=white) [![CI](https://github.com/raj75114043-design/ai-ml-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/raj75114043-design/ai-ml-portfolio/actions/workflows/ci.yml) [![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://raj-knowledge-graph-builder.streamlit.app) [![Docker](https://img.shields.io/badge/Docker-ghcr.io-2496ED?style=flat-square&logo=docker&logoColor=white)](https://github.com/users/raj75114043-design/packages/container/package/ai-ml-portfolio%2Fknowledge-graph-builder)

An end-to-end pipeline that turns tabular operational data into a validated knowledge graph,
with **ontology design**, **fuzzy entity resolution**, **schema validation** and **idempotent
Cypher export** for Neo4j.

## Ontology

```mermaid
graph LR
    S[Site] -- HAS_ACTIVITY --> A[Activity]
    A -- USES_MATERIAL --> M[Material]
    M -- SUPPLIED_BY --> V[Vendor]
```

## Pipeline

| Step | Implementation |
|---|---|
| Ingest | CSV sources for vendors, materials and activities |
| Entity resolution | Name normalisation + RapidFuzz token-sort matching; low-confidence matches go to manual review |
| Validation | Every edge checked against the ontology |
| Export | `MERGE` statements so reloads never create duplicates |
| Query | Multi-hop traversal Site → Activity → Material → Vendor |

Example: `"BETA POWER SYSTEMS LTD"` and `"Alpha Infra Suppliers"` are resolved to the correct
master vendors despite casing, suffix and spelling differences.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## When to Use a Graph vs SQL vs RAG

| Need | Best fit |
|---|---|
| Filtering and aggregation | Relational database |
| Multi-hop relationship traversal | Knowledge graph |
| Answers from unstructured documents | RAG |

> All data in this repository is synthetic.

## Web Application

Streamlit interface that renders the graph, runs multi-hop queries per site, shows every entity-resolution decision with its confidence, and exports a Neo4j Cypher load script.

## Run, Deploy and Test

**Web application**

```bash
cd knowledge-graph-builder
pip install -r requirements.txt
streamlit run app.py
```

Live demo: https://raj-knowledge-graph-builder.streamlit.app

**Docker**

```bash
docker build -t knowledge-graph-builder .
docker run -p 8501:8501 knowledge-graph-builder
# or pull the published image
docker pull ghcr.io/raj75114043-design/ai-ml-portfolio/knowledge-graph-builder:latest
```

**Tests**

```bash
pytest -q
```

Every push to the [`ai-ml-portfolio`](https://github.com/raj75114043-design/ai-ml-portfolio) repository runs this project's tests through GitHub Actions and publishes its Docker image to GitHub Container Registry.
