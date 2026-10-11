# MLOps Pipeline Template

![Python 3.10+](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) ![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white) ![License MIT](https://img.shields.io/badge/License_MIT-FF3B3B?style=flat-square&logo=opensourceinitiative&logoColor=white) [![CI](https://github.com/raj75114043-design/ai-ml-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/raj75114043-design/ai-ml-portfolio/actions/workflows/ci.yml) [![Docker](https://img.shields.io/badge/Docker-ghcr.io-2496ED?style=flat-square&logo=docker&logoColor=white)](https://github.com/users/raj75114043-design/packages/container/package/ai-ml-portfolio%2Fmlops-pipeline-template)

A production-style template covering the full model lifecycle: **training with a quality gate,
experiment tracking, artefact versioning, a validated REST API, automated tests, containerisation,
CI and Kubernetes deployment**.

## Pipeline

```mermaid
flowchart LR
    T[Train] --> G{Quality Gate F1 >= 0.90}
    G -- pass --> A[Versioned Artefacts + MLflow]
    G -- fail --> X[Stop Pipeline]
    A --> S[FastAPI Service]
    S --> P[pytest]
    P --> D[Docker Image]
    D --> K[Kubernetes: 2 replicas, probes, limits]
```

## Components

| Stage | Implementation |
|---|---|
| Training | Random Forest with fixed seed and stratified split |
| Quality gate | Pipeline fails if F1 is below threshold |
| Tracking | MLflow parameters, metrics and artefacts (optional) |
| Serving | FastAPI with schema validation and `/health` endpoint |
| Testing | pytest for health, prediction and input validation |
| CI | GitHub Actions: train → test → build |
| Deployment | Kubernetes Deployment and Service with readiness/liveness probes |

## Quick Start

```bash
pip install -r requirements.txt
python -m src.train
pytest -q
uvicorn src.serve:app --reload        # http://localhost:8000/docs
```

### Docker

```bash
docker build -t mlops-pipeline-template .
docker run -p 8000:8000 mlops-pipeline-template
```

## Run, Deploy and Test

**Docker**

```bash
docker build -t mlops-pipeline-template .
docker run -p 8000:8000 mlops-pipeline-template
# or pull the published image
docker pull ghcr.io/raj75114043-design/ai-ml-portfolio/mlops-pipeline-template:latest
```

**Tests**

```bash
pytest -q
```

Every push to the [`ai-ml-portfolio`](https://github.com/raj75114043-design/ai-ml-portfolio) repository runs this project's tests through GitHub Actions and publishes its Docker image to GitHub Container Registry.
