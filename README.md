# Agentic AI for Resource-Constrained Campus SOCs

Hands-on materials for the WiCyS 2026 workshop:

> **Agentic AI for Resource-Constrained Campus SOCs: Hands-On, Interpretable Defense**

Colleges that serve low-income and underrepresented communities often face higher cybersecurity risks because of limited budgets, small IT teams, and outdated systems. This repository provides an **open, containerized pipeline** that runs on standard laptops and is designed for teaching and experimentation in resource-constrained campus SOCs, workforce programs, and student cyber clubs.

The stack focuses on:

* **Interpretability:** simple features + rule-based logic + a tiny ML second-opinion model.
* **Privacy:** aggressive data reduction and anonymization.
* **Fairness and language equity:** basic group metrics and threshold tuning notebooks.
* **Human-in-the-loop defense:** explicit actions (`allow`, `queue_for_review`, `escalate`) and helpdesk runbooks.

All materials are intended to be used with **anonymized or synthetic logs**. No production systems are required.

## Repository Structure

```text
collector/           # FastAPI service: log ingestion + anonymization + feature extraction
detector/            # FastAPI service: interpretable scoring + optional tiny ML model
notebooks/           # JupyterLab notebooks for pipeline exploration and fairness checks
  01_intro_pipeline.ipynb
  02_feature_extraction.ipynb
  03_threshold_tuning_equity.ipynb
data/                # Seed datasets + ingested_events.jsonl log file
  seed_lms_events.csv
  seed_email_events.csv
docs/
  runbooks/
    helpdesk_triage.md
  threshold_changes.md
  overrides_log.md
governance_checklist.md
docker-compose.yml
README.md
LICENSE
```

## Quick Start

### Prerequisites

* Docker Desktop or a compatible Docker engine
* Git
* A laptop with at least 4 GB of RAM

### Clone and Run

```bash
git clone <your-repo-url> wicys-soc-workshop
cd wicys-soc-workshop

# Build containers
docker compose build

# Run the full stack
docker compose up
```

Services:

* **JupyterLab:** `http://localhost:8888`

  * Token: `wicys2026` (configurable in `docker-compose.yml`)
* **Collector API:** `http://localhost:8001`
* **Detector API:** `http://localhost:8000`

## Loading Seed Datasets and Generating Events

The repository includes synthetic, anonymized seed datasets:

* `data/seed_lms_events.csv`
* `data/seed_email_events.csv`

These mimic:

* LMS events such as logins, submissions, and discussion posts
* Email gateway events such as reminders and suspicious emails

You can either ingest them via a notebook or POST rows directly to `/ingest`:

```bash
curl -X POST http://localhost:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{
        "user_id": "student123",
        "email": "student123@example.edu",
        "source": "email_gateway",
        "message": "URGENT: Your campus password will expire today. Click this link to keep your account active and receive a gift card.",
        "event_type": "suspicious_email",
        "language": "en"
      }'
```

All ingested events are appended to:

* `data/ingested_events.jsonl`

This file is used by the fairness and threshold-tuning notebook.

> **Note:** The workshop uses **exports or synthetic logs**, not live LMS or email integrations. In production, you would adapt your own exporters to call the collector API.

## Interpretable Detector and Tiny ML Guardrail

The detector service (`detector/app.py`) combines:

1. A **rule-based core**

   * Features: `contains_link`, `contains_password`, `contains_urgent`, `contains_reward`, `len_message`
   * Produces a risk score in `[0, 1]`
   * Returns `label` and `action` for triage

2. An optional **tiny ML logistic model**

   * Controlled by the `USE_ML` environment variable (`0` or `1`)
   * Computes a second-opinion risk score from the same features
   * If the ML score is higher, it can raise the final risk score and add a short explanation
   * Any error or misconfiguration falls back safely to the rule-based logic

To enable the ML second opinion, set this for the detector service in `docker-compose.yml`:

```yaml
environment:
  - USE_ML=1
```

## Governance, Runbooks, and Fairness

### Governance Checklist

`governance_checklist.md` provides a testable list of:

* Data reduction and anonymization practices
* Transparency and interpretability requirements
* Fairness and language-equity checks
* Human-in-the-loop triage policies
* Safe operation for resource-limited environments
* Documentation and reproducibility expectations

### Helpdesk Triage Runbook

`docs/runbooks/helpdesk_triage.md` describes:

* How to handle `allow`, `queue_for_review`, and `escalate` actions
* When and how to override the detector
* How to document overrides in `docs/overrides_log.md`
* How to communicate with end users about suspicious messages

### Fairness and Threshold Tuning Notebook

`notebooks/03_threshold_tuning_equity.ipynb`:

* Loads `data/ingested_events.jsonl`
* Computes metrics by language and domain
* Plots risk score distributions per group
* Sweeps thresholds and reports escalation-rate gaps

Use this notebook once per term or per exercise to decide:

* Whether thresholds should be adjusted
* Whether any group is being disproportionately escalated

Document decisions in `docs/threshold_changes.md`.

## Adaptation for Local Contexts

You can adapt this stack for:

* Community colleges and regional universities
* Cybersecurity workforce programs
* Student cyber clubs and competitions
* Courses in networking, security, or data science

Common adaptations:

* Replace `seed_*` CSVs with your own **anonymized** campus exports
* Add new rules or features in `collector/app.py` and `detector/app.py`
* Extend notebooks with additional fairness metrics or visualizations

Always ensure that:

* No direct identifiers appear in logs or notebooks
* Local policies and regulations are followed for data handling

## Licensing and Open Access

This project is intended to be released under a permissive license such as MIT or Apache-2.0 so that institutions without commercial cybersecurity tools can freely adopt and adapt it.

Add a `LICENSE` file to this repository to formalize the license choice.
