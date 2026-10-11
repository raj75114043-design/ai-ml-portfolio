# Pharma OOS / OOT Analytics

![Python 3.10+](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![GxP](https://img.shields.io/badge/GxP-2E7D32?style=flat-square&logo=checkmarx&logoColor=white) ![License MIT](https://img.shields.io/badge/License_MIT-FF3B3B?style=flat-square&logo=opensourceinitiative&logoColor=white) [![CI](https://github.com/raj75114043-design/ai-ml-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/raj75114043-design/ai-ml-portfolio/actions/workflows/ci.yml) [![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://raj-pharma-oos-oot-analytics.streamlit.app) [![Docker](https://img.shields.io/badge/Docker-ghcr.io-2496ED?style=flat-square&logo=docker&logoColor=white)](https://github.com/users/raj75114043-design/packages/container/package/ai-ml-portfolio%2Fpharma-oos-oot-analytics)

Statistical trending of batch release results for oral solid dosage products, separating
**Out-of-Specification (OOS)** results from **Out-of-Trend (OOT)** signals, supporting
APQR and Continued Process Verification (CPV) workflows.

## OOS vs OOT

| Signal | Definition | Action |
|---|---|---|
| **OOS** | Result outside registered specification limits | Phase I / Phase II investigation per OOS SOP |
| **OOT** | Within specification but statistically unusual against process history | Trend review and assessment |

## Trend Rules Implemented

| Rule | Description |
|---|---|
| Rule 1 | One point beyond ±3σ |
| Rule 2 | Two of three consecutive points beyond ±2σ on the same side |
| Rule 4 | Eight consecutive points on the same side of the mean |
| Rule 5 | Six points steadily increasing or decreasing |

Control limits are derived from a baseline period using the moving-range estimate of sigma,
and process capability (Cpk) is reported for the APQR.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

Outputs: `outputs/flagged_batches.csv` and `outputs/assay_control_chart.png`.

## Data Integrity Considerations (ALCOA+)

In a regulated deployment, source data is read from validated systems (LIMS / QMS), all
calculations are version-controlled and reproducible, and outputs carry an audit trail in line
with 21 CFR Part 11 and EU Annex 11. This repository illustrates the analytics only.

> All batch data in this repository is synthetic and does not represent any real product or company.

## Web Application

Streamlit dashboard: upload a batch results CSV (or use the sample), pick the quality attribute and baseline, and review the control chart, OOS and OOT tables, Cpk and a downloadable flagged-batch report.

## Run, Deploy and Test

**Web application**

```bash
cd pharma-oos-oot-analytics
pip install -r requirements.txt
streamlit run app.py
```

Live demo: https://raj-pharma-oos-oot-analytics.streamlit.app

**Docker**

```bash
docker build -t pharma-oos-oot-analytics .
docker run -p 8501:8501 pharma-oos-oot-analytics
# or pull the published image
docker pull ghcr.io/raj75114043-design/ai-ml-portfolio/pharma-oos-oot-analytics:latest
```

**Tests**

```bash
pytest -q
```

Every push to the [`ai-ml-portfolio`](https://github.com/raj75114043-design/ai-ml-portfolio) repository runs this project's tests through GitHub Actions and publishes its Docker image to GitHub Container Registry.
