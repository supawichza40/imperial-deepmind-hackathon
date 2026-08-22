# ADR-010 — FastAPI + PWA frontend, replacing Streamlit

**Date:** 22 Aug 2026
**Status:** accepted
**Supersedes:** ADR-003 (Streamlit for the consent UI)

## Context
ADR-003 chose Streamlit for the fastest path to a demo UI. The project now requires:
1. A **web app** (not a script) — installable, with a proper frontend.
2. **PWA support** — manifest + service worker for "Add to Home Screen".
3. **TDD** — tests must be written before implementation, which requires a testable API layer.

Streamlit cannot satisfy these: it has no PWA support, its server-side session model is hard to test with TDD, and it doesn't produce an installable web app.

## Decision
Replace Streamlit with:
- **FastAPI** backend — serves static files + REST API endpoints.
- **Plain HTML/CSS/JS frontend** — no build tools, no framework, just static files.
- **PWA** — manifest.json + service-worker.js for installability and offline shell caching.
- **pytest** — TDD test suite for core modules and API endpoints.

The core Python modules (detector, sanitiser, reasoner, audit, types, fixtures) are **unchanged** — they are pure functions called by the API layer.

## Consequences
- The API is testable in isolation with FastAPI's `TestClient` and mocked external services.
- The frontend is a static SPA — no build step, no npm, just files in `static/`.
- PWA installability adds demo value: "Add to Home Screen" feels like a real product.
- The service worker caches the UI shell for offline load, but API calls still require localhost.
- Slightly more code than Streamlit (API layer + frontend), but each piece is independently testable.
- ADR-003 is superseded but not deleted — it documents the original reasoning.

## Related
- [Architecture spec](../specs/architecture.md) — full architecture
- [API spec](../specs/api.md) — endpoint definitions
- [Testing spec](../specs/testing.md) — TDD approach
- [ADR-003](003-streamlit-ui.md) — superseded decision