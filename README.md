# Agentic AI for Resource-Constrained Campus SOCs

Hands-on materials for the **WiCyS 2026** workshop:

**Agentic AI for Resource-Constrained Campus SOCs: Hands-On, Interpretable Defense**

This repository provides an open, containerized workflow for **interpretable, human-in-the-loop security triage** in resource-constrained campus environments. It is designed for teaching, experimentation, and workforce development using **anonymized or synthetic data** rather than live production systems.

Designed and developed by **Samuel Addington**.

Colleges and universities that serve low-income and underrepresented communities often face elevated cybersecurity risk while operating with limited budgets, small IT teams, and aging infrastructure. This project focuses on workflows that small teams can realistically **run, inspect, explain, and improve**.

## Key Features

- **Interpretability**  
  Transparent feature extraction, rule-based scoring, and short human-readable explanations.

- **Bounded AI Assistance**  
  The workflow returns explicit triage actions:
  - `allow`
  - `queue_for_review`
  - `escalate`

- **Optional Lightweight ML Support**  
  A tiny ML second-opinion model can raise the risk score, while the rule-based path remains the safe fallback.

- **Privacy by Design**  
  Data reduction and anonymization are built into the ingestion workflow.

- **Fairness and Language-Equity Review**  
  Group-level review by language and domain, supported by threshold-tuning notebooks.

- **Human-in-the-Loop Governance**  
  Helpdesk runbooks, threshold-change logs, override records, and governance checklists are included in the repo.

## Repository Structure

```text
collector/           # FastAPI service: log ingestion, anonymization, feature extraction, and optional web UI
detector/            # FastAPI service: interpretable scoring + optional tiny ML model
notebooks/           # JupyterLab notebooks for pipeline exploration and fairness checks
  notebooks/
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

Prerequisites
Docker Desktop or a compatible Docker engine

- Git

- A laptop with at least 4 GB of RAM

Quick Start
Clone the repo:

```text
git clone https://github.com/SamAddington/wicys-soc-workshop
cd wicys-soc-workshop
```

Build the containers:

```text
docker compose build
```

Start the stack:

```text
docker compose up
```

Services
Once the stack is running, these services should be available:

- JupyterLab: http://localhost:8888
Token: wicys2026
(configurable in docker-compose.yml)

- Collector API: http://localhost:8001

- Collector Web UI: http://localhost:8001/

- Detector API: http://localhost:8000

Web Demo Interface
The easiest way to use the workflow during the workshop is through the attendee-facing web interface:

Open: http://localhost:8001/

The web interface allows you to:

- load suspicious and benign sample events

- submit events without using curl

inspect the returned:

- risk score

- label

-action

-explanation

interpret the bounded triage output in a workshop-friendly format

This is the recommended interface for live demonstrations and attendee use.

Seed Datasets
The repository includes synthetic, anonymized seed datasets:

- data/seed_lms_events.csv

- data/seed_email_events.csv

These mimic:

- LMS events such as logins, submissions, and discussion posts

- email gateway events such as reminders and suspicious emails

All ingested events are appended to:

data/ingested_events.jsonl

This file is used by the feature-extraction and fairness / threshold-tuning notebooks.

Note 
The workshop uses exported or synthetic logs, not live LMS or email integrations. In a production environment, you would adapt your own exporter or pipeline to call the collector API.

Loading Events 
You can submit events in two ways:

Recommended: use the web interface at http://localhost:8001/

Advanced / API usage: send JSON directly to /ingest

Example API Request (Bash)
curl -X POST http://localhost:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{
        "user_id": "student123",
        "email": "student123@example.edu",
        "source": "email_gateway",
        "message": "URGENT: Your campus password will expire today. Click this link http://fake-reset.example to keep your account active and receive a gift card.",
        "event_type": "suspicious_email",
        "language": "en"
      }'
Example API Request (Windows Command Prompt)
curl -X POST http://localhost:8001/ingest -H "Content-Type: application/json" -d "{\"user_id\":\"student123\",\"email\":\"student123@example.edu\",\"source\":\"email_gateway\",\"message\":\"URGENT: Your campus password will expire today. Click this link http://fake-reset.example to keep your account active and receive a gift card.\",\"event_type\":\"suspicious_email\",\"language\":\"en\"}"
Expected Response Shape
A successful response will look similar to this:

```text
{
  "status": "ok",
  "detector_result": {
    "risk_score": 0.8,
    "label": "high_risk",
    "action": "escalate",
    "explanation": "Mentions passwords or passphrases. / Uses urgent language (e.g., 'urgent', 'immediately'). / Offers rewards such as gift cards or bonuses."
  },
  "human_triage_hint": "Mentions passwords or passphrases. / Uses urgent language (e.g., 'urgent', 'immediately'). / Offers rewards such as gift cards or bonuses."
}
```

** Detector Logic **
The detector service (detector/app.py) combines:

1. Rule-Based Core
The rule-based detector uses transparent features such as:

- contains_link
- contains_password
- contains_urgent
- contains_reward
- len_message

It produces:

-  risk score in [0, 1]
- a triage label
- a bounded action
- a short explanation

2. Optional Tiny ML Second Opinion
The detector can optionally apply a small logistic-style second-opinion model.

Controlled by the USE_ML environment variable (0 or 1)

Uses the same extracted features as the rule-based core

Can raise the final risk score if it detects a stronger suspicious pattern

Falls back safely to rule-based behavior if the ML path is disabled or fails

To enable the ML second opinion, set this for the detector service in docker-compose.yml:

```text
environment:
  - USE_ML=1
```

Governance, Runbooks, and Fairness
Governance Checklist
governance_checklist.md provides a testable list of:

- data reduction and anonymization practices

- transparency and interpretability requirements

- fairness and language-equity checks

- human-in-the-loop triage policies

- safe operation for resource-limited environments

- documentation and reproducibility expectations

Helpdesk Triage Runbook
docs/runbooks/helpdesk_triage.md describes:

how to handle allow, queue_for_review, and escalate

when and how to override the detector

how to document overrides in docs/overrides_log.md

how to communicate with end users about suspicious messages

Fairness and Threshold-Tuning Notebook
notebooks/notebooks/03_threshold_tuning_equity.ipynb:

loads data/ingested_events.jsonl

computes metrics by language and domain

plots risk-score distributions per group

sweeps thresholds and reports escalation-rate gaps

Use this notebook to decide:

whether thresholds should be adjusted

whether any group is being disproportionately escalated

whether changes should be documented in docs/threshold_changes.md

Suggested Workshop Flow
A typical live demo or lab session can follow this sequence:

Start the Docker stack

Open the web interface at http://localhost:8001/

Submit a suspicious sample event

Review the returned risk score, label, action, and explanation

Submit a benign sample event

Compare outputs

Open the notebooks to inspect:

extracted features

stored JSONL events

threshold tuning

fairness checks

Review the helpdesk runbook and governance checklist

Adaptation for Local Contexts
You can adapt this stack for:

community colleges and regional universities

cybersecurity workforce programs

student cyber clubs and competitions

courses in networking, security, or data science

Common adaptations include:

replacing seed_* CSVs with your own anonymized campus exports

adding new rules or features in collector/app.py and detector/app.py

extending notebooks with additional fairness metrics or visualizations

using the web interface for student labs instead of direct API calls

Always ensure that:

no direct identifiers appear in logs or notebooks

local policies and regulations are followed for data handling

synthetic or properly de-identified data are used for public demos and coursework

Troubleshooting
JupyterLab Keeps Restarting
If the notebooks container exits repeatedly with a message about running as root, make sure the Jupyter command includes:

--allow-root

and uses the current token setting format:

--IdentityProvider.token=...

Then rebuild the notebooks container.

localhost:8888 Refuses to Connect
Check whether the notebooks container is running:

```text
docker compose ps
docker compose logs notebooks --tail=50
localhost:8001 or localhost:8000 Refuses to Connect
```

Verify the collector and detector services:

```text
curl http://localhost:8001/health
curl http://localhost:8000/health
```

Expected response:

```text
{"status":"up"}
```

Windows curl Command Fails
If you are using Windows Command Prompt, use the single-line example shown above.
The multi-line Bash-style example with \ line continuation will not work correctly in cmd.exe.

Web UI Does Not Load
If http://localhost:8001/ does not open:

- confirm that the collector container is running

- confirm that the collector service exposes port 8001

- verify that the static UI files are copied into the collector image

- rebuild the collector container if needed

** License **
This project is released under the terms described in the LICENSE file.

** Acknowledgment of Scope ** 
This repository is intended for:

- workshop instruction

- classroom use

- security workflow experimentation

- governance-oriented demonstrations of bounded AI assistance

It is not a production SOC platform, and it should not be represented as a substitute for enterprise SIEM, SOAR, or institutional incident-response infrastructure.

