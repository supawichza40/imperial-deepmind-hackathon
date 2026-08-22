# Privacy Gate — API Spec

**What this is:** REST API definition for the Privacy Gate backend.
**Base URL:** `http://localhost:8000`
**Content type:** `application/json` for all API requests and responses.
**Implements:** [architecture spec](architecture.md) §4.2.
**Frontend contract:** [ui.md](ui.md). Detect and sanitise bodies in this file still use the old five-type / `[REDACTED]` shape. Match [ui.md](ui.md) §6 and §10 when you wire FastAPI to the live panel.

---

## 1. Conventions

- All endpoints are prefixed with `/api`.
- All requests and responses are JSON (`Content-Type: application/json`).
- Error responses use a consistent shape (see §7).
- The API is stateless — no server-side session. Each request carries all data it needs.
- All endpoints respond to `GET /api/{endpoint}` with OpenAPI docs at `/docs` (FastAPI auto-generated).

---

## 2. Endpoints

### 2.1 GET /api/documents

List available fixture documents.

**Request:** no body, no params.

**Response:** `200 OK`
```json
{
  "documents": [
    {"id": "payslip", "name": "Payslip — July 2026", "text": "PAYSLIP — July 2026\nEmployee: A. Okafor\n..."},
    {"id": "bank_statement", "name": "Bank Statement — Jul 2026", "text": "BANK STATEMENT — Account 12345678\n..."}
  ]
}
```

**Spec traceability:** FR-1, FR-2.

---

### 2.2 POST /api/detect

Run sensitive-field detection on one or more documents. Returns spans per document.

**Request:**
```json
{
  "documents": [
    {"id": "payslip", "text": "PAYSLIP — July 2026\nEmployee: A. Okafor\n..."}
  ]
}
```

`documents` is an array of `{id, text}` objects. At least one is required. `text` is the full document string.

**Response:** `200 OK`
```json
{
  "results": {
    "payslip": {
      "text": "ACME LTD  —  PAYSLIP\n...",
      "spans": [
        {"id": "name-1", "type": "name", "start": 50, "end": 59, "value": "A. Okafor", "kind": "text", "image_id": "", "bbox": null},
        {"id": "ni-1", "type": "ni_number", "start": 72, "end": 84, "value": "QQ123456C", "kind": "text", "image_id": "", "bbox": null}
      ],
      "images": [
        {"id": "staff-photo", "alt": "Staff photo", "data_url": "data:image/svg+xml;utf8,..."}
      ],
      "documentName": "payslip",
      "fallback_triggered": false,
      "warning": ""
    }
  }
}
```

`results` is a dict keyed by document id. Each value includes:
- `text`: the original document text (required — the frontend needs it to highlight spans against the same string the offsets were measured on).
- `spans`: list of Span objects with `id`, `type`, `start`, `end`, `value`, `kind`, `image_id`, `bbox` (see [ui.md §6.1](ui.md)).
- `images`: list of image objects for image/signature spans.
- `documentName`: download stem.
- `fallback_triggered` + `warning`: DetectionResult metadata.

**Privacy note:** `text` is the original document. This is sent from browser to localhost FastAPI only (same-origin). It never leaves the machine. The backend uses it for detection only.

**Error cases:**
- `400` — `documents` array is empty or missing.
- `422` — a document is missing `id` or `text`.

**Spec traceability:** FR-4 through FR-11. Calls `detector.detect(text)` per document.

---

### 2.3 POST /api/sanitise (optional — headless/CLI utility)

**Note:** The primary redaction path is **client-side** in the browser via `PrivacyExport.mount()` (see [ui.md §5.1](ui.md)). This endpoint is kept for headless testing, CLI use, and non-browser clients. The browser does not call it in the normal demo flow.

Produce the sanitised payload from document text, detected spans, and the user's toggle decisions.

**Request:**
```json
{
  "documents": [
    {"id": "payslip", "text": "ACME LTD  —  PAYSLIP\n..."}
  ],
  "spans": {
    "payslip": [
      {"id": "name-1", "type": "name", "start": 50, "end": 59, "value": "A. Okafor", "kind": "text"}
    ]
  },
  "toggles": {
    "name": "blacklabel",
    "address": "blacklabel",
    "ni_number": "blacklabel",
    "account_number": "blacklabel"
  },
  "passphrase": null
}
```

- `toggles`: dict of `{type: "keep"|"blacklabel"|"encrypt"}` (ADR-012).
- `passphrase`: required if any toggle is `encrypt`. Never logged.

**Response:** `200 OK`
```json
{
  "sanitised_payload": "--- DOCUMENT: PAYSLIP ---\nPAYSLIP — July 2026\nEmployee: [REDACTED]\nNI Number: [REDACTED]\n...\nGross Pay: £2,840.00\n..."
}
```

The `sanitised_payload` is the concatenated, redacted text. Blocked spans are replaced with `[REDACTED]`. Shared spans are left intact. Multi-document payloads are joined with the delimiter from spec §3.5.

**Error cases:**
- `400` — `consent` is missing.
- `422` — a span references a doc id not in `documents`.

Note: if both `shared_types` and `blocked_types` are empty (no consent decision), the payload is returned unredacted — this is valid (the user chose to share nothing sensitive because nothing was flagged). If all types are blocked, the payload is fully redacted — also valid (FR-26 applies at the UI level, not the API level; the API returns whatever the consent decision produces).

**Spec traceability:** FR-15, FR-16. Calls `sanitiser.sanitise_multi(documents, spans, blocked_types)` which handles per-document redaction and concatenation with delimiters (see design §3.4).

---

### 2.4 POST /api/reason

Send the sanitised payload to Gemini 3.7 Flash for inconsistency detection.

**Request:**
```json
{
  "sanitised_payload": "--- DOCUMENT: PAYSLIP ---\n...\n--- DOCUMENT: BANK STATEMENT ---\n..."
}
```

**Response:** `200 OK`
```json
{
  "inconsistency_detected": true,
  "analysis": "The payslip shows net pay of £2,427.40 for July 2026, but the bank statement shows a deposit of £2,480.00 on 25 Jul 26. The difference of £52.60 is unexplained.",
  "draft_letter": "Dear Pelham Consulting,\nI am writing to query a discrepancy..."
}
```

**Error cases:**
- `400` — `sanitised_payload` is empty or missing.
- `200` with fallback body — if Gemini API call fails after all retries, `reasoner.py` catches the exception internally and returns a fallback `GeminiResult` with `inconsistency_detected=false`, `analysis="Cloud reasoning failed: {error message}"`, `draft_letter=""`. The API returns `200` with this fallback body, not `502`. This is deliberate: the user still gets a usable response (the sanitised payload was valid), and the demo doesn't crash on a Gemini outage.

**Spec traceability:** FR-17 through FR-21. Calls `reasoner.reason(payload)`.

**Privacy guarantee:** this endpoint only receives the sanitised payload. It never has access to the original document text. The backend enforces this by design — `reasoner.py` only accepts a string, not the full document.

---

### 2.5 POST /api/audit

Build the audit log from detection results and consent decision.

**Request:**
```json
{
  "spans": {
    "payslip": [
      {"type": "name", "start": 25, "end": 34, "text": "A. Okafor"},
      {"type": "income", "start": 140, "end": 151, "text": "£2,840.00"}
    ]
  },
  "consent": {
    "shared_types": ["income"],
    "blocked_types": ["name", "ni_number", "address", "account_number"]
  },
  "detection_results": {
    "payslip": {
      "spans": [],
      "fallback_triggered": false,
      "warning": ""
    }
  }
}
```

- `spans`: dict of `{doc_id: list[Span]}` — the detected spans per document.
- `consent`: `ConsentDecision`.
- `detection_results`: dict of `{doc_id: DetectionResult}` — used to add fallback entries (FR-10).

**Response:** `200 OK`
```json
{
  "audit_log": [
    {"field_type": "name", "decision": "kept_local", "approved_by": "user", "details": ""},
    {"field_type": "income", "decision": "shared", "approved_by": "user", "details": ""},
    {"field_type": "ni_number", "decision": "kept_local", "approved_by": "user", "details": ""},
    {"field_type": "address", "decision": "kept_local", "approved_by": "user", "details": ""},
    {"field_type": "account_number", "decision": "kept_local", "approved_by": "user", "details": ""}
  ]
}
```

If a fallback was triggered, an additional entry appears:
```json
{"field_type": "detector", "decision": "fallback", "approved_by": "system", "details": "Local model unavailable — used regex-only detection."}
```

**Spec traceability:** FR-22, FR-23, FR-10. Calls `audit.build_audit()`.

---

### 2.6 POST /api/chat  (STRETCH)

Free-form conversation over the sanitised payload. Same privacy boundary as `/api/reason`: this endpoint never receives original text.

**Request:**
```json
{
  "sanitised_payload": "--- DOCUMENT: PAYSLIP ---\n...",
  "history": [
    {"role": "user", "content": "Does my income cover the rent?"},
    {"role": "model", "content": "Comfortably, on the figures you shared..."}
  ],
  "message": "What account is the salary paid into?"
}
```

**Response:** `200 OK`
```json
{
  "reply": "I cannot see that. The account number was hidden before this document reached me, so there is nothing here for me to read.",
  "cited_fields": [],
  "refused_field_types": ["account_number"]
}
```

- `reply` is plain text for display.
- `cited_fields` names the visible fields the answer used, for the citation chips in the UI.
- `refused_field_types` is non-empty when the question needed redacted material. The UI renders those differently (wood left border, per ui.md).

**Error cases:**
- `400` when `sanitised_payload` or `message` is empty.
- `200` with a fallback body when Gemini fails after retries: `reply` explains the cloud call failed, `cited_fields` and `refused_field_types` empty. Same reasoning as §2.4: never crash the demo on a Gemini outage.

**System prompt addition:** instruct the model that `[REDACTED]` and `[BLACKLABELED ...]` markers are fields the user deliberately withheld, that it must say plainly it cannot see them, and that it must never infer or guess their contents.

**Spec traceability:** FR-40 through FR-43. Calls `reasoner.chat(payload, history, message)`.

---

## 3. Frontend interaction flow

The frontend calls these endpoints in sequence, matching the demo flow (spec §5):

```
1. GET  /api/documents           → populate document selector
2. POST /api/detect              → get spans, render highlights
3. (user adjusts consent checkboxes in UI — no API call)
4. POST /api/sanitise            → get sanitised payload, show preview (PITCH MOMENT)
5. POST /api/reason              → get Gemini analysis + draft letter
6. POST /api/audit               → get audit log, display
```

Steps 4-6 can be combined into a single "Send to Gemini" button click in the UI: the frontend calls sanitise → reason → audit in sequence.

---

## 4. Static file serving

Multi-page routes (ADR-013). The app has three entry points, not a single SPA.

| Route | Serves |
|---|---|
| `GET /` | Redirect to `/vault/` |
| `GET /vault/` | `app/static/vault/index.html` |
| `GET /privacy-export/` | `app/static/privacy-export/index.html` |
| `GET /theme/` | `app/static/theme/index.html` |
| `GET /static/{path}` | Files in `app/static/` directory |
| `GET /manifest.json` | `app/static/manifest.json` (for PWA registration) |
| `GET /service-worker.js` | Service worker (served at root for `/` scope) |

FastAPI's `StaticFiles` mount handles `/static/{path}`. The three route directories (`/vault/`, `/privacy-export/`, `/theme/`) are served via `StaticFiles` mounts at their respective paths. Root `/` redirects to `/vault/`. The service worker is served at root for `/` scope.

---

## 5. CORS

Since the frontend and API are served from the same origin (`localhost:8000`), CORS is not needed. If the frontend were served separately (e.g. during development), add:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
```

For the hackathon, same-origin is simpler and more secure.

---

## 6. Request/response schemas (Pydantic)

FastAPI uses Pydantic models for request validation and auto-generated OpenAPI docs. These mirror the TypedDicts in `types.py` but are Pydantic `BaseModel` classes for the API layer.

```python
from pydantic import BaseModel
from typing import Literal

class DocumentInput(BaseModel):
    id: str
    text: str

class DetectRequest(BaseModel):
    documents: list[DocumentInput]

class SpanModel(BaseModel):
    id: str = ""
    type: str
    start: int
    end: int
    value: str = ""
    kind: str = "text"
    image_id: str = ""
    bbox: list[float] | None = None

class ImageModel(BaseModel):
    id: str
    alt: str = ""
    data_url: str = ""

class DetectionResultModel(BaseModel):
    text: str = ""
    spans: list[SpanModel] = []
    images: list[ImageModel] = []
    documentName: str = ""
    fallback_triggered: bool = False
    warning: str = ""

class ConsentRequest(BaseModel):
    toggles: dict[str, str]       # {type: "keep"|"blacklabel"|"encrypt"}
    passphrase: str | None = None

class SanitiseRequest(BaseModel):
    documents: list[DocumentInput]
    spans: dict[str, list[SpanModel]]
    toggles: dict[str, str]
    passphrase: str | None = None

class ReasonRequest(BaseModel):
    sanitised_payload: str

class AuditRequest(BaseModel):
    spans: dict[str, list[SpanModel]]
    toggles: dict[str, str]
    detection_results: dict[str, DetectionResultModel] = {}

class GeminiResultModel(BaseModel):
    inconsistency_detected: bool
    analysis: str
    draft_letter: str

class AuditEntryModel(BaseModel):
    field_type: str
    decision: str
    approved_by: str
    details: str
```

These are defined in `api/main.py` (or `api/contracts.py`). They do NOT replace `types.py` — the core modules still use TypedDicts. The API layer converts between Pydantic models and TypedDicts at the boundary.

**Key changes from original spec (ADR-011, ADR-012):**
- `SpanModel` now has `id`, `value` (was `text`), `kind`, `image_id`, `bbox`.
- `ConsentRequest` uses `toggles` + `passphrase` (was `shared_types`/`blocked_types`).
- `DetectionResultModel` now includes `text`, `images`, `documentName`.

---

## 7. Error response shape

All error responses follow this shape:

```json
{
  "error": "human-readable error message",
  "detail": "optional technical detail"
}
```

HTTP status codes:
- `400` — client error (missing/invalid input)
- `422` — validation error (Pydantic rejected the body, FastAPI auto-generates this)
- `500` — unexpected server error

Note: Gemini API failures are handled internally by `reasoner.py` — the API returns `200` with a fallback body, never `502`.

---

## 8. OpenAPI documentation

FastAPI auto-generates OpenAPI docs at:
- `GET /docs` — Swagger UI
- `GET /redoc` — ReDoc

These are available in development but can be disabled in production with `app = FastAPI(docs_url=None, redoc_url=None)`.

---

## Related

- [UI spec](ui.md) — live frontend contract. Prefer this for request bodies.
- [Architecture spec](architecture.md) — system architecture
- [Requirements spec](privacy-gate.md) — functional requirements, data contracts
- [Design doc](design.md) — core module designs
- [Testing spec](testing.md) — TDD approach for API tests