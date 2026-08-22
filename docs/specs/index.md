# Specs index

Current project truth: what the system is, what it must do, and how to build it.

| Spec | Status | What it covers |
|---|---|---|
| [privacy-gate.md](privacy-gate.md) | active | Functional requirements, data contracts, fixtures, regex patterns, prompt templates |
| [ui.md](ui.md) | **active, source of truth for frontend** | Live screens, span/toggle/QR contracts, what FastAPI must serve. Use this for the backend spec. |
| [design.md](design.md) | active for detector algorithms, stale for UI | Core module designs: detector, sanitiser, reasoner, audit. Streamlit layout is obsolete. |
| [architecture.md](architecture.md) | active | System architecture: FastAPI + PWA frontend, process model, directory structure, security boundaries |
| [api.md](api.md) | active, adapt bodies to ui.md §10 | REST API endpoint definitions, request/response schemas, error shapes |
| [testing.md](testing.md) | active | TDD strategy, test definitions per module, fixtures, test priorities |
| [development-plan.md](development-plan.md) | active | Feature breakdown, TDD task sequence, 3-person team assignment, timeline, risks |