# ADR-013 — Multi-page routes and client-side redaction

**Date:** 22 Aug 2026
**Status:** accepted
**Supersedes:** the single-SPA architecture in ADR-010's frontend section

## Context
ADR-010 specified a single `index.html` SPA. The built frontend has three separate entry points:
- `/vault/` — folder management, ACL, lock, QR share
- `/privacy-export/` — consent panel, redaction preview, download
- `/theme/` — design token playground (not a product screen)

Additionally, the built UI performs redaction client-side via `PrivacyExport.mount()`. The browser applies toggles to spans and produces sanitised text locally. The `POST /api/sanitise` endpoint is not needed for the primary flow — it becomes a headless/CLI utility.

## Decision
- **Multi-page routes:** FastAPI serves three static directories, not one SPA. Root `/` redirects to `/vault/`.
- **Client-side redaction is the primary path:** the browser does redaction. `POST /api/sanitise` is kept as an optional headless utility.
- **PWA manifest and service worker** must cover all three routes (scope at root).

## Consequences
- Architecture spec's static/ layout and PWA section must be updated.
- API spec's §4 routes table must change.
- Testing spec's API tests for `/api/sanitise` become optional/headless tests.
- Service worker scope must be at root to cache all three routes.

## Related
- [ADR-010](010-fastapi-pwa.md) — superseded (frontend architecture portion)
- [UI spec §2, §10](../specs/ui.md) — routes and pipeline