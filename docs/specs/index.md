# Specs index

Current project truth. If two specs disagree, later ADRs and the live UI win.

Authority order: [ui.md](ui.md) (built frontend) → [privacy-gate.md](privacy-gate.md) + ADR-011/012/013 → [api.md](api.md) → [architecture.md](architecture.md) → [design.md](design.md) (algorithms only).

| Spec | Status | What it covers |
|---|---|---|
| [privacy-gate.md](privacy-gate.md) | active | Functional requirements, data contracts, fixtures, regex patterns, prompt templates |
| [design.md](design.md) | algorithms only, UI stale | Detector merge and reasoner. Do not copy Streamlit or five-type consent. |
| [architecture.md](architecture.md) | active | System architecture: FastAPI + multi-page PWA, process model, directory structure, security boundaries |
| [api.md](api.md) | active | REST API endpoint definitions, request/response schemas, error shapes |
| [testing.md](testing.md) | active | TDD strategy, test definitions per module, fixtures, test priorities |
| [development-plan.md](development-plan.md) | active | Feature breakdown, TDD task sequence, 3-person team assignment, timeline, risks |
| [ui.md](ui.md) | active, built | Live frontend: vault, export panel, QR share, theme. Data contracts the UI consumes. Ground truth for span shape, field types, consent model, redaction tokens |
| [security.md](security.md) | active | Threat model, cryptographic parameters, vault ACL, QR share security, honest limitations |