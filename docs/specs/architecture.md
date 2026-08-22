# Privacy Gate — Architecture Spec

**What this is:** system architecture for the Privacy Gate web application with PWA support.
**Implements:** [requirements spec](privacy-gate.md), [design doc](design.md).
**Supersedes:** ADR-003 (Streamlit) — see ADR-010.

---

## 1. Architecture overview

```mermaid
flowchart TB
    subgraph BROWSER["PWA FRONTEND — browser, installable"]
        SW[service-worker.js<br/>offline shell cache]
        VAULT[vault/index.html + vault.js<br/>folders, ACL, QR share]
        EXPORT[privacy-export/index.html + privacy-export.js<br/>consent panel, redaction preview]
        MAN[manifest.json<br/>PWA install metadata]
    end

    subgraph SERVER["FASTAPI BACKEND — localhost"]
        API[api/main.py<br/>REST endpoints + static serving]
        DET[detector.py<br/>regex + Gemma]
        REA[reasoner.py<br/>Gemini cloud call]
        AUD[audit.py<br/>audit log builder]
        TYP[types.py<br/>shared TypedDicts]
        FIX[fixtures.py<br/>synthetic documents]
    end

    subgraph CLOUD["CLOUD — sees only sanitised payload"]
        GEM[Gemini 3.7 Flash<br/>Interactions API]
    end

    subgraph LOCAL["OLLAMA — localhost"]
        OLL[gemma4:e2b<br/>native /api/generate]
    end

    VAULT -->|REST: POST /api/detect etc.| API
    EXPORT -->|REST: POST /api/reason| API
    API --> DET --> OLL
    API --> REA --> GEM
    API --> AUD
    SW -.->|cache static shell| VAULT
    SW -.->|cache static shell| EXPORT
    MAN -.->|install prompt| VAULT
```

**Architecture:** FastAPI backend serves a multi-page PWA frontend (`/vault/`, `/privacy-export/`, `/theme/`). The browser does redaction client-side via `PrivacyExport.mount()`. The backend handles detection (Ollama), reasoning (Gemini), and audit. See [ui.md](ui.md) for the live frontend contract. ADR-013.

---

## 2. Process model

```
User's machine:
  ┌─────────────────────────────────────────────┐
  │  Browser (PWA)                              │
  │    index.html + app.js + styles.css         │
  │    service-worker.js (caches static shell)  │
  │    manifest.json (PWA metadata)             │
  └──────────────┬──────────────────────────────┘
                 │ HTTP (localhost:8000)
  ┌──────────────▼──────────────────────────────┐
  │  FastAPI server (uvicorn)                   │
  │    Serves: static files + /api/* endpoints  │
  └──────┬───────────────┬──────────────────────┘
         │               │
  ┌──────▼─────┐  ┌──────▼──────────────────────┐
  │  Ollama    │  │  Gemini API (cloud)         │
  │  :11434    │  │  via google-genai SDK       │
  │  (local)   │  │  (sanitised payload only)   │
  └────────────┘  └─────────────────────────────┘
```

- **Single process:** FastAPI serves both static files (frontend) and API endpoints from one `uvicorn` process.
- **No separate frontend build step.** Plain HTML/CSS/JS — no React, no bundler, no npm. This is a 2-hour build.
- **PWA:** manifest.json + service worker enable "Add to Home Screen" and offline static shell caching. The API calls still require localhost connectivity (Ollama + FastAPI), but the UI shell loads without network.

---

## 3. Directory structure

```
app/
├── types.py              # Shared TypedDicts
├── fixtures.py           # Synthetic documents
├── detector.py           # Regex + Gemma detection
├── sanitiser.py          # Reverse-offset redaction (optional — browser does client-side)
├── reasoner.py           # Gemini cloud call
├── audit.py              # Audit log builder
├── main.py               # CLI entry point (kept for headless testing)
├── export/               # Export zip + redaction (built by teammate)
│   ├── redact.py          # apply_export — █ blacklabel + [ENCRYPTED] 
│   ├── fields.py          # 9 field types, default_toggles
│   ├── pack.py            # build_zip_bytes
│   ├── crypto.py          # AES-GCM, PBKDF2
│   └── sample.py          # Canonical payslip fixture
├── access/               # Vault, ACL, QR share (built by teammate)
│   ├── acl.py             # Role ladder, inheritance
│   ├── share.py           # Signed pointer (#s=)
│   ├── transfer.py        # Instant transfer (#t=) gzip JSON
│   ├── totp.py            # TOTP for two-step delete
│   └── store.py           # Vault state
├── api/
│   ├── __init__.py
│   ├── contracts.py       # Pydantic models (shared with frontend mock builder)
│   └── main.py            # FastAPI app: static files + REST endpoints
├── static/                # Multi-page frontend (ADR-013)
│   ├── vault/             # /vault/ — folder management, ACL, QR share
│   │   ├── index.html
│   │   ├── vault.js        # PrivacyVault.mount
│   │   ├── qr.js           # PrivacyQr.svg
│   │   └── qrcodegen.js    # Nayuki QR encoder
│   ├── privacy-export/    # /privacy-export/ — consent panel, redaction preview
│   │   ├── index.html
│   │   ├── privacy-export.js  # PrivacyExport.mount
│   │   └── demo-payload.js    # window.PRIVACY_EXPORT_DEMO
│   ├── theme/             # /theme/ — design tokens (not a product screen)
│   │   ├── tokens.js
│   │   ├── tokens.css
│   │   └── components.css
│   ├── manifest.json      # PWA install metadata
│   ├── service-worker.js  # Offline shell cache (scope: /)
│   └── icons/
│       ├── icon-192.png
│       └── icon-512.png
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_detector.py
    ├── test_sanitiser.py
    ├── test_reasoner.py
    ├── test_audit.py
    ├── test_api.py
    └── test_e2e.py
```

**Key points:**
- Core modules (`types.py` through `audit.py`) are unchanged from the design doc — pure functions, no web framework dependency.
- `api/main.py` is the only new Python code — a thin FastAPI wrapper that calls the existing modules.
- `static/` is the PWA frontend — plain HTML/CSS/JS, no build step.
- `tests/` is first-class — TDD means tests are written before implementation.

---

## 4. Layer responsibilities

### 4.1 Frontend (PWA) — `static/` (multi-page, already built)

| Component | Responsibility |
|---|---|
| `vault/index.html` + `vault.js` | Folder management, ACL, lock, QR share, guest open |
| `privacy-export/index.html` + `privacy-export.js` | Consent panel (PrivacyExport.mount), redaction preview, download |
| `theme/index.html` + `tokens.js/css` | Design token playground (not a product screen) |
| `manifest.json` | PWA metadata: name, icons, display mode, theme colour |
| `service-worker.js` | Cache static shell for offline load (scope: `/`) |

**Frontend state machine:**
```
IDLE → DOCUMENT_SELECTED → DETECTING → DETECTED → CONSENT_PENDING
  → SANITISED (client-side) → REASONING → COMPLETE
```

The browser does redaction client-side via `PrivacyExport.mount()` — no `/api/sanitise` call needed in the normal flow. See [ui.md](ui.md) for the full frontend contract.

### 4.2 API layer — `api/main.py`

| Endpoint | Method | Purpose | Spec FR |
|---|---|---|---|
| `/` | GET | Redirect to `/vault/` | — |
| `/vault/` | GET | Serve vault page (built) | — |
| `/privacy-export/` | GET | Serve export panel (built) | — |
| `/static/{path}` | GET | Serve static files | — |
| `/api/documents` | GET | List available fixture documents | FR-1, FR-2 |
| `/api/detect` | POST | Run detection on a document, return spans + text + images | FR-4–FR-11 |
| `/api/sanitise` | POST | (optional) Headless sanitisation — browser does redaction client-side | FR-15 |
| `/api/reason` | POST | Send sanitised payload to Gemini, return analysis | FR-17–FR-21 |
| `/api/audit` | POST | Build audit log from spans + toggles + detection results | FR-22 |

**Why separate endpoints instead of one pipeline call:** each stage is a user-initiated step in the UI. The user must see the spans, approve consent, and see the sanitised payload before anything goes to Gemini. A single pipeline endpoint would skip the human gate (violating FR-14).

**API statelessness:** the API is stateless. Each request carries the data it needs (document text, spans, consent decision). No server-side session. The frontend holds state between calls.

### 4.3 Core modules — minor addition

`types.py`, `fixtures.py`, `detector.py`, `reasoner.py`, `audit.py` are identical to the design doc — pure functions, no changes. `sanitiser.py` gains one additional function: `sanitise_multi()` (already defined in design doc §3.4) which handles multi-document concatenation. The API layer always calls `sanitise_multi()` — even for a single document, the payload is wrapped with the `--- DOCUMENT: X ---` delimiter. This simplifies the API (one code path) and is consistent with the response examples in the API spec. No other module changes.

### 4.4 External services

| Service | Address | Network | Purpose |
|---|---|---|---|
| Ollama | `localhost:11434` | local | Gemma 4 E2B inference |
| Gemini API | `generativelanguage.googleapis.com` | cloud | Gemini 3.7 Flash reasoning |
| FastAPI | `localhost:8000` | local | Serves frontend + API |

---

## 5. PWA configuration

### 5.1 manifest.json
```json
{
  "name": "Privacy Gate",
  "short_name": "PrivacyGate",
  "description": "Assisted redaction with human approval",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#111214",
  "theme_color": "#1a7f4b",
  "icons": [
    {"src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}
  ]
}
```

### 5.2 service-worker.js
- Caches the static shell on install: vault page, export panel, theme, manifest, icons.
- Serves from cache on fetch when offline (cache-first strategy for static assets).
- Does NOT cache API responses — those require the local server.
- Registration: `navigator.serviceWorker.register('/service-worker.js')` in vault/export pages. The service worker is served at root (not `/static/`) so its scope covers `/` — a service worker at `/static/service-worker.js` can only intercept `/static/*`, not the root navigation request.

### 5.3 What "offline" means for this PWA
- The **UI shell** loads offline (cached by service worker).
- The **API calls** require the FastAPI server running on localhost — which in turn requires Ollama for detection and internet for Gemini.
- The **detection step** works with wifi off (Ollama is local) but requires the FastAPI server to be running.
- The **reasoning step** requires internet (Gemini API).
- PWA installability is the primary demo value: "Add to Home Screen" makes it feel like a real app, not a web page.

---

## 6. Dependencies

### 6.1 Python (additions to `starter/requirements.txt`)
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
httpx>=0.27.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

- `fastapi` — API framework
- `uvicorn` — ASGI server
- `httpx` — async HTTP client (used by TestClient for API tests)
- `pytest` + `pytest-asyncio` — test runner for TDD

### 6.2 Frontend
No build tools. Plain HTML/CSS/JS. No npm, no bundler.

### 6.3 PWA icons
Two placeholder PNG icons (192×192 and 512×512). Can be generated with any tool or be simple solid-colour squares with a "PG" label for the hackathon.

---

## 7. Startup and run commands

```bash
# Install deps
pip install -r starter/requirements.txt

# Set up environment
cp starter/.env.example .env
# Edit .env: GEMINI_API_KEY=...

# Pull local model
ollama pull gemma4:e2b

# Run tests (TDD — write tests first, then implement)
pytest app/tests/ -v

# Start the server
uvicorn app.api.main:app --reload --port 8000

# Open the app
open http://localhost:8000
```

---

## 8. Demo deployment

| Step | Command |
|---|---|
| Warm the model | `ollama run gemma4:e2b ""` (during setup) |
| Start the server | `uvicorn app.api.main:app --port 8000` |
| Open the app | `http://localhost:8000` |
| Install as PWA | Chrome → Install → "Privacy Gate" appears as app |

---

## 9. Alignment with existing docs

### 9.1 What changes from the design doc

| Design doc says | Architecture spec says | Why |
|---|---|---|
| Streamlit `app.py` orchestrates everything | FastAPI `api/main.py` + multi-page static frontend | Web app + PWA requirement (ADR-010, ADR-013) |
| Session state in `st.session_state` | State in frontend JS + localStorage | No server-side session |
| One monolithic file (`app.py`) | API layer + multi-page frontend split | Testable API, installable PWA |
| No test framework | `pytest` with TDD | Testing spec requirement |
| 5 field types | 9 field types (ADR-011) | Built code has 9 |
| Binary consent (shared/blocked) | 3-state consent (keep/blacklabel/encrypt) (ADR-012) | Built code has 3 states |
| `[REDACTED]` token | `█` bars + `[ENCRYPTED ...]` | Built code uses these |

### 9.2 What stays the same

- Core modules: `types.py`, `fixtures.py`, `detector.py`, `sanitiser.py`, `reasoner.py`, `audit.py` — unchanged.
- Data contracts: `Span`, `DetectionResult`, `ConsentDecision`, `AuditEntry`, `GeminiResult` — unchanged.
- Algorithms: two-pass merge, best-match offsets, reverse-offset redaction, JSON fence stripping — unchanged.
- Prompts, regex patterns, fixtures — unchanged.
- Privacy boundary: originals never leave the device — unchanged.

### 9.3 Spec impact

The requirements spec (FR-12, FR-16) references "Streamlit" — these are updated to "web UI". FR-12 says "colour-coded by type in Streamlit" → "colour-coded by type in the web UI". No functional requirement changes.

---

## 10. Security boundaries

```
┌─────────────────────────────────────────────────────────────┐
│ BROWSER (PWA)                                               │
│   Can: display documents, call localhost API                │
│   Cannot: call Gemini directly, call Ollama directly        │
└──────────────────────┬──────────────────────────────────────┘
                       │ localhost only
┌──────────────────────▼──────────────────────────────────────┐
│ FASTAPI BACKEND                                             │
│   Can: call Ollama (local), call Gemini (cloud)             │
│   Enforces: only sanitised payload sent to Gemini           │
│   Never logs: API keys, original document text              │
└──────┬───────────────────────────────┬──────────────────────┘
       │ localhost                     │ HTTPS
┌──────▼──────────┐           ┌────────▼──────────────────────┐
│ OLLAMA (local)  │           │ GEMINI API (cloud)            │
│ Sees: full text │           │ Sees: sanitised payload ONLY  │
└─────────────────┘           └───────────────────────────────┘
```

- The browser never has the Gemini API key. All cloud calls go through the FastAPI backend.
- The backend never sends original text to Gemini. The sanitiser runs before `reasoner.py` is called.
- Ollama sees the full text — it's local, that's the point.

---

## Related

- [UI spec](ui.md) — live screens and JSON the frontend already consumes
- [Requirements spec](privacy-gate.md) — functional requirements
- [Design doc](design.md) — module designs (core modules unchanged)
- [API spec](api.md) — endpoint definitions
- [Testing spec](testing.md) — TDD approach
- [ADR-010](../decisions/010-fastapi-pwa.md) — rationale for the architecture shift