# Support Ticket Triage — NLP

![Python 3.10+](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white) ![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white) ![NLP](https://img.shields.io/badge/NLP-Classification_%2B_NER-FF3B3B?style=flat-square) [![CI](https://github.com/raj75114043-design/ai-ml-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/raj75114043-design/ai-ml-portfolio/actions/workflows/ci.yml) [![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://raj-support-ticket-nlp.streamlit.app) [![Docker](https://img.shields.io/badge/Docker-ghcr.io-2496ED?style=flat-square&logo=docker&logoColor=white)](https://github.com/users/raj75114043-design/packages/container/package/ai-ml-portfolio%2Fsupport-ticket-nlp)

Automatic triage of IT support tickets: **category classification**, **entity extraction** (ticket IDs,
error codes, invoices, IPs, emails, products), **priority detection** and **routing to the right team**,
with a confidence threshold that sends uncertain tickets to manual triage.

## Business Problem

Service desks lose hours each day reading and re-routing tickets. Mis-routed tickets breach SLAs, and
key identifiers buried in free text must be copied by hand into downstream systems.

## Approach

| Component | Implementation |
|---|---|
| Classifier | Word (1–2) + character (3–5) TF-IDF features with class-balanced logistic regression |
| Evaluation | Stratified hold-out, macro-F1 and per-class precision/recall |
| Entity extraction | Precise regular expressions and a product gazetteer for IDs that must be exact |
| Priority | Urgency-phrase detection (P1 / P3) |
| Routing | Category → team mapping; confidence below 50% goes to manual triage |
| Data | 1,500 synthetic tickets across five categories with ~6% deliberate label noise |

```mermaid
flowchart LR
    T[Ticket Text] --> C[TF-IDF + Logistic Regression]
    T --> N[Entity Extraction]
    T --> P[Priority Detection]
    C --> R{Confidence ≥ 50%?}
    R -- yes --> Team[Route to Team]
    R -- no --> M[Manual Triage]
    N & P --> O[Structured Ticket]
```

## Results

Output of the reproducible run (`python main.py`):

```
Trained on 1200 tickets; macro-F1 on 300 held-out tickets = 0.937
              precision  recall  f1-score
Access            0.933   0.918     0.926
Billing           0.934   0.950     0.942
Hardware          0.889   0.949     0.918
Network           0.982   0.918     0.949
Software          0.949   0.949     0.949
macro avg         0.938   0.937     0.937
weighted avg      0.938   0.937     0.937

Example: Urgent: Outlook crashes with error E512 on startup. Ticket INC204211, contact me at priya@example.com
 -> Software (86%) | Application Support | P1 - High
 -> entities: PRODUCT=Outlook, ERROR_CODE=E512, TICKET_ID=INC204211, EMAIL=priya@example.com
```

## Run, Deploy and Test

**Web application**

```bash
cd support-ticket-nlp
pip install -r requirements.txt
streamlit run app.py
```

Live demo: https://raj-support-ticket-nlp.streamlit.app

**Docker**

```bash
docker build -t support-ticket-nlp .
docker run -p 8501:8501 support-ticket-nlp
# or pull the published image
docker pull ghcr.io/raj75114043-design/ai-ml-portfolio/support-ticket-nlp:latest
```

**Tests**

```bash
pytest -q
```

Every push to the [`ai-ml-portfolio`](https://github.com/raj75114043-design/ai-ml-portfolio) repository runs this project's tests through GitHub Actions and publishes its Docker image to GitHub Container Registry.

> All tickets in this repository are synthetic.
