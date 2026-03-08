# Governance Checklist for Resource-Constrained Campus SOCs

*Agentic AI for Resource-Constrained Campus SOCs: Hands-On, Interpretable Defense*  
**Version 1.0 – WiCyS 2026 Workshop Release**

This checklist operationalizes the governance, privacy, fairness, and human-in-the-loop commitments described in the workshop abstract. It is intended for community colleges, minority-serving institutions, rural campuses, and any environment where cybersecurity teams operate with limited staffing and budgets.

The checklist is divided into six domains, each with testable items that can be implemented using the Docker images and notebooks provided in this workshop.

## 1. Data Reduction and Anonymization

### 1.1 Inputs
- [ ] Remove all direct identifiers (full emails, names, student IDs) before ingestion.
- [ ] Only store hashed identifiers in the `anon_user` field.
- [ ] Extract email domain only when needed for risk analysis.
- [ ] Accept logs only from approved export sources (LMS, email gateway, helpdesk system).

### 1.2 Storage
- [ ] Store only minimal fields needed for classification.
- [ ] Confirm that `ingested_events.jsonl` contains no sensitive fields.
- [ ] Ensure retention does not exceed campus policy.

### 1.3 Access Control
- [ ] Notebook access secured by token or password.
- [ ] Only designated analysts or instructors may run equity or threshold-tuning notebooks.
- [ ] Students or interns must work only with anonymized logs.

## 2. Transparency and Interpretability

### 2.1 Rule Logic
- [ ] Document all risk factors used in `detector/app.py`.
- [ ] Provide plain-language explanations for each indicator.
- [ ] Keep risk weights and thresholds in visible code or notebook cells.

### 2.2 Explainability Outputs
- [ ] Confirm each `/score` response includes a brief explanation in natural language.
- [ ] Explanations must be suitable for helpdesk or student workers with minimal training.
- [ ] Analysts must validate explanations before modifying thresholds.

## 3. Fairness and Language Equity

### 3.1 Data Logging for Equity Review
- [ ] Ensure language field is captured for every event when available.
- [ ] Store group-level metadata (domain, language) but not identity-level data.
- [ ] Log detection outcomes (`low_risk`, `medium_risk`, `high_risk`) per event.

### 3.2 Fairness Evaluation
- [ ] Run the fairness notebook at least once per semester.
- [ ] Compare risk-score distributions across language groups.
- [ ] Compare risk-score distributions across email domains.
- [ ] Identify disparities in false-positive or escalation rates using simple metrics.

### 3.3 Equity Adjustments
- [ ] Adjust thresholds if they disproportionately flag specific groups.
- [ ] Document threshold changes in `docs/threshold_changes.md`.
- [ ] Provide justification for each change using evidence from notebooks.

## 4. Human-in-the-Loop Triage

### 4.1 Escalation Path
- [ ] High-risk events must always be reviewed by a human before action.
- [ ] Medium-risk events go to a review queue for junior analysts or trained student workers.
- [ ] Low-risk events do not require human review but remain logged for audit.

### 4.2 Override Authority
- [ ] Analysts may override detector labels but must record rationale.
- [ ] Overrides logged in `docs/overrides_log.md`.

### 4.3 Reviewer Guidelines
- [ ] Reviewers must consult runbooks for LMS phishing indicators, email spoofing red flags, and foreign-language message handling.
- [ ] All reviewers receive training aligned with local campus accessibility and language policies.

## 5. Safe Operation and Misuse Prevention

### 5.1 Pipeline Integrity
- [ ] Verify collector and detector containers before deployment.
- [ ] Do not allow students to run containers with elevated host privileges.
- [ ] Disable outbound network access from containers unless explicitly needed.

### 5.2 Misuse Prevention
- [ ] Prevent unauthorized users from modifying feature weights or thresholds.
- [ ] Review logs for unusual ingestion patterns.
- [ ] Protect scoring endpoints from external exposure.

### 5.3 Resource Constraints
- [ ] Ensure CPU and memory limits are defined if required for local environments.
- [ ] System must run on standard laptops without raising resource warnings.

## 6. Documentation, Training, and Reproducibility

### 6.1 Documentation Artifacts
- [ ] `README.md` includes full setup instructions.
- [ ] `governance_checklist.md` included.
- [ ] Runbooks included in `docs/runbooks/`.
- [ ] Seed datasets included in `data/`.

### 6.2 Reproducibility
- [ ] All notebooks run deterministically with the provided seed logs.
- [ ] All threshold-tuning steps are reproducible using the same CSVs.
- [ ] Users can clone the repo and run the full pipeline on laptops quickly.

### 6.3 Licensing and Open Access
- [ ] Release materials under a permissive open-source license.
- [ ] Do not include proprietary vendor code.
- [ ] Ensure all content is accessible to institutions without commercial cybersecurity tools.
