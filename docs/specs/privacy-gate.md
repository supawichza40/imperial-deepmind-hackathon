# Privacy Gate — Requirements Spec

**What this is:** the current spec an agent can build from in ~2 hours with no further questions.
**Source:** derived from `docs/visual/2026-08-22-privacy-gate.html`, reviewed by Gemini and Claude (see [dev-log/spec-review-01.md](../dev-log/spec-review-01.md)).
**Scope:** functional requirements + data contracts + fixtures + prompts. No design.

---

## 1. What we're building

A document redaction gate. User drops in a sensitive document → a local model finds private fields → user ticks what can leave → only the approved, redacted text goes to a cloud model for reasoning → an audit log records what stayed and what went.

Two models, one hard boundary:
- **Local:** Gemma 4 E2B via Ollama (offline, on-device). Finds sensitive fields. Returns matched text + type, never prose, never offsets.
- **Cloud:** Gemini 3.7 Flash via `google-genai` Interactions API. Reasons over the redacted payload only.

The boundary is the product. Originals never leave the machine.

**Framing rule:** "assisted redaction with human approval" — never "guaranteed anonymisation".

**UI framework:** Web app (FastAPI backend + static HTML/CSS/JS frontend, PWA-installable). See [architecture spec](architecture.md). Supersedes ADR-003 (Streamlit).

**Env var:** `GEMINI_API_KEY` (read by `starter/utils.py:get_client()`, already built).

---

## 2. Functional requirements

MUST = ship it. SHOULD = nice if time allows. COULD = cut first.

### 2.1 Input
- **FR-1 (MUST):** Accept one text document as input. Default: a synthetic payslip (see §7 fixtures).
- **FR-2 (MUST):** Use pre-seeded synthetic documents only. No real personal data. No file upload / PDF parsing — hardcoded strings in a fixtures file.
- **FR-3 (SHOULD):** Accept a second document (bank statement) for cross-document comparison. If built, both documents are concatenated into the sanitised payload with a delimiter (see §3.5).

### 2.2 Detection (local, on-device)
- **FR-4 (MUST):** Detect sensitive fields on-device before any network call.
- **FR-5 (MUST):** Use regex baseline. The exact patterns are in §8. Covers: NI numbers, UK postcodes, emails, account numbers.
- **FR-6 (MUST):** Use Gemma 4 E2B for names in context and other sensitive fields regex can't catch (income figures, dates). Gemma returns `{text, type}` pairs — matched substrings, NOT character offsets. Python resolves offsets via `str.find()`.
- **FR-7 (MUST):** The detector merges regex + Gemma results into a single span map: `[{type, start, end, text}]` where `start`/`end` are zero-based char offsets resolved in Python.
- **FR-8 (MUST):** Call Gemma via Ollama native `/api/generate` with `think: false`, `num_predict: 200`, `format: "json"`. System prompt in §9.1.
- **FR-9 (MUST):** Detector is a pure function: `detect(text: str) -> list[Span]`. No side effects, no network (Ollama runs locally).
- **FR-10 (MUST):** If Ollama is unreachable or times out after **3 seconds**, fall back to regex-only detection silently. Log a warning to the audit trail.
- **FR-11 (MUST):** Parse Gemma's JSON output defensively — strip markdown wrappers (` ```json ... ``` `), handle trailing commas, handle malformed JSON gracefully. If parsing fails, treat as no Gemma results (regex-only).

### 2.3 Consent
- **FR-12 (MUST):** Show the document with detected spans highlighted (colour-coded by type in the web UI).
- **FR-13 (MUST):** User approves per **field type** (e.g. "share income, hide name"), not per span. One checkbox per detected type.
- **FR-14 (MUST):** Nothing crosses the gate until the user clicks "Send approved to Gemini."
- **FR-15 (MUST):** Produce the **sanitised payload**: document text with blocked spans replaced by `[REDACTED]`. Replacement is applied in **reverse offset order** (rightmost first) to preserve earlier offsets. Overlapping spans are merged before replacement (see §3.6).
- **FR-16 (MUST):** Show the user the exact sanitised payload in a text area before it is sent. This is the pitch moment of the demo.

### 2.4 Cloud reasoning
- **FR-17 (MUST):** Send only the sanitised payload to Gemini 3.7 Flash via `client.interactions.create()`. System prompt in §9.2.
- **FR-18 (MUST):** Original document text must never be sent to the cloud. No exceptions.
- **FR-19 (MUST):** Gemini's prompt must explicitly instruct it to reason *only* over visible text and ignore `[REDACTED]` tokens — not speculate about what was removed.
- **FR-20 (MUST):** Gemini performs one reasoning task: find an inconsistency between the documents (or within one document if only one is provided). Explain it in plain language. Response schema in §3.7.
- **FR-21 (SHOULD):** Gemini also drafts a response/explanation letter (field `draft_letter` in the response schema).

### 2.4a Conversation (STRETCH, cut first)
- **FR-40 (STRETCH):** After sanitisation, the user may open a chat about the sanitised payload and ask free-form questions. Same payload, same privacy boundary as FR-17 and FR-18.
- **FR-41 (STRETCH):** The chat carries turn history. Each request sends the sanitised payload plus prior turns. The original text is never part of the history.
- **FR-42 (STRETCH):** When a question can only be answered from redacted material, the reply must say it cannot see that field and name the field type. It must never guess. This is the demo's proof that the gate is real.
- **FR-43 (STRETCH):** Each answer cites which visible fields it used, so the user can check the reasoning against what they approved.

Why this is worth building last and showing first: a judge who watches the model refuse to answer a question about a hidden field has seen the privacy claim tested live, rather than described.

### 2.5 Audit log
- **FR-22 (MUST):** Record, per field type: whether it was kept local or shared, and that the user approved.
- **FR-23 (MUST):** Display the audit log showing what stayed local and what was shared.
- **FR-24 (MUST):** The audit log is never cut from the demo.

### 2.6 Pipeline
- **FR-25 (MUST):** Stages run in order: intake → detect → consent → sanitise → cloud reason → audit.
- **FR-26 (MUST):** Halt before the cloud stage if the user approved nothing.

---

## 3. Data contracts

### 3.1 Span (detector output element)
```python
class Span(TypedDict):
    id: str           # stable identifier, e.g. "name-1"
    type: str         # field type label, see §4
    start: int        # zero-based char offset into source text (inclusive)
    end: int          # zero-based char offset (exclusive)
    value: str        # the matched substring (renamed from "text" — see ADR-011)
    kind: str         # "text" (default), "signature", or "personal_image"
    image_id: str     # for image spans: links to Image.id; empty for text spans
    bbox: list[float] # for image spans: [x, y, w, h] as 0-1 fractions; None for text
```

Image/signature spans use `start: 0, end: 0` (no text offset) and point at an image via `image_id`.

### 3.2 Span map (full detector output)
```json
[
  {"type": "name",           "start": 9,   "end": 18,  "text": "A. Okafor"},
  {"type": "ni_number",      "start": 30,  "end": 42,  "text": "QQ123456C"},
  {"type": "address",        "start": 52,  "end": 70,  "text": "14 Pelham St, SW7"},
  {"type": "account_number", "start": 80,  "end": 95,  "text": "12345678"},
  {"type": "income",         "start": 108, "end": 120, "text": "£2,840.00"}
]
```

### 3.3 Consent decision
```json
{
  "toggles": {
    "name": "blacklabel",
    "address": "blacklabel",
    "ni_number": "blacklabel",
    "account_number": "blacklabel",
    "email": "blacklabel",
    "phone": "blacklabel",
    "date_of_birth": "blacklabel",
    "signature": "blacklabel",
    "personal_image": "blacklabel"
  },
  "passphrase": null
}
```

3-state toggle per type (ADR-012): `keep` (visible/shared), `blacklabel` (blocked, `█` bars), `encrypt` (blocked, `[ENCRYPTED ...]` with AES-GCM). `passphrase` required when any toggle is `encrypt`. Never logged.

For audit compatibility: `keep` → `shared`, `blacklabel`/`encrypt` → `kept_local`.

### 3.4 Sanitised payload
Source document string with every span whose toggle is `blacklabel` replaced by `█` bars (same length) and every `encrypt` span replaced by `[ENCRYPTED ...]`. `keep` spans are left intact. Replacements applied in reverse offset order. This is the only text that crosses the gate.

Do NOT emit `[REDACTED]` — the built UI and export code use `█` and `[ENCRYPTED ...]` (ADR-012).

### 3.5 Multi-document payload (if FR-3 is built)
If two documents are used, concatenate their sanitised texts with a delimiter:
```
--- DOCUMENT: PAYSLIP ---
<sanitised payslip text>
--- DOCUMENT: BANK STATEMENT ---
<sanitised bank statement text>
```
Consent is per field type **globally** (not per document). Both documents share the same `shared_types`/`blocked_types`.

### 3.6 Span overlap / merge rule
1. Merge overlapping or nested spans of the **same type** into one span (earliest start, latest end).
2. For overlapping spans of **different types**, keep the longer span, drop the shorter.
3. After merging, apply replacements in **reverse order** (highest `start` first) so earlier offsets remain valid.
4. If two spans share the same `start`, the one with the larger `end` wins.

### 3.7 Gemini response schema
```json
{
  "inconsistency_detected": true,
  "analysis": "The payslip shows gross pay of £2,840.00 for July 2026, but the bank statement shows a corresponding deposit of £2,480.00. The difference of £360.00 is unexplained.",
  "draft_letter": "Dear HR, I am writing to query a discrepancy..."
}
```
If no inconsistency is found, `inconsistency_detected` is `false` and `analysis` explains what was checked.

### 3.8 Audit entry
```json
{
  "field_type": "name",
  "decision": "kept_local",
  "approved_by": "user",
  "details": ""
}
```
One entry per field type. `decision` is `kept_local`, `shared`, or `fallback` (for detector fallback warnings). `approved_by` is `user` for consent decisions, `system` for fallback entries. `details` carries the warning text for fallback entries, empty otherwise.

### 3.9 Function signatures (for parallel agent work)
```python
# Detector — local, pure function. Returns DetectionResult with spans + fallback metadata.
def detect(text: str) -> DetectionResult: ...

# Sanitiser — deterministic, pure function (optional — browser does redaction client-side)
def sanitise(text: str, spans: list[Span], toggles: dict[str, str], passphrase: str | None = None) -> str: ...

# Consent — UI produces this (PrivacyExport.mount in the browser)
# toggles: {type: "keep"|"blacklabel"|"encrypt"}, passphrase: str | None

# Cloud reasoner — calls Gemini
def reason(payload: str) -> GeminiResult: ...

# Audit — produces the log. Takes per-doc spans + per-doc detection results.
def build_audit(all_spans: dict[str, list[Span]], toggles: dict[str, str],
                detection_results: dict[str, DetectionResult] | None = None) -> list[AuditEntry]: ...
```

`DetectionResult` is `{"spans": list[Span], "fallback_triggered": bool, "warning": str}`. See design doc §3.1.

---

## 4. Field types

9 identity field types, all default `blacklabel`. Pay figures (gross, net, tax) are NOT a field type — they stay visible because they are untyped payload data, which is how the Gemini inconsistency check works without any toggle.

| Type | Detected by | Example | Default |
|---|---|---|---|
| `name` | Gemma | "A. Okafor" | blacklabel |
| `address` | Gemma + regex (postcode) | "14 Pelham St, SW7" | blacklabel |
| `ni_number` | regex | "QQ123456C" | blacklabel |
| `account_number` | regex | "4417" | blacklabel |
| `email` | regex | "a.okafor@example.com" | blacklabel |
| `phone` | regex | "07700 900123" | blacklabel |
| `date_of_birth` | Gemma | "14 Mar 1998" | blacklabel |
| `signature` | Gemma | "A. Okafor" | blacklabel |
| `personal_image` | Gemma / images | staff photo | blacklabel |

See ADR-011 (supersedes ADR-004's 5-type reduction). Canonical list in `app/export/fields.py`.

---

## 5. Demo flow (2 minutes)

This is a requirement — 20% of the rubric.

1. App loads with pre-seeded payslip (+ bank statement if time). No file upload.
2. Click "Detect sensitive fields." Gemma + regex highlights them on screen.
3. User ticks: "share income, hide identity and account."
4. **Show the sanitised payload about to be sent.** This is the pitch moment.
5. Click "Send to Gemini." Gemini finds the income figures don't match.
6. Gemini's analysis + draft letter displayed.
7. Audit log shown: what stayed local, what was shared.

**Cut order if short on time:** second document (drop to payslip only) → draft letter → live highlight animation. Never cut the audit log.

---

## 6. Non-functional requirements

- **NFR-1 (MUST):** Local detection works with wifi off.
- **NFR-2 (MUST):** No original text leaves the device. Only sanitised payload is transmitted.
- **NFR-3 (MUST):** Gemma is called for `{text, type}` pairs, not prose (10.8 tok/s on E2B — every token is a tenth of a second). `num_predict` capped at 200.
- **NFR-4 (MUST):** Keep the model warm before demoing (`ollama run gemma4:e2b ""` during setup).
- **NFR-5 (MUST):** Ollama call has a **3-second timeout**. If exceeded, fall back to regex-only.
- **NFR-6 (MUST):** Cloud call uses retry-with-backoff for 429/503 (already in `starter/utils.py`).
- **NFR-7 (MUST):** No API keys committed or logged.
- **NFR-8 (MUST):** No PDF parsing, no OCR, no file upload. Hardcoded synthetic text only.

---

## 7. Fixture data (synthetic documents)

These are the exact strings the app loads. No real personal data. The payslip and bank statement contain a **planted inconsistency**: gross pay £2,840.00 on the payslip vs deposit £2,480.00 on the bank statement.

### 7.1 Payslip (canonical — matches `app/export/sample.py`)
```
ACME LTD  —  PAYSLIP
Period: July 2026

Employee: A. Okafor
NI number: QQ123456C
Address: 14 Pelham St, SW7
Email: a.okafor@example.com
Phone: 07700 900123
Account: 4417
Date of birth: 14 Mar 1998

Gross pay: £2,840.00
Tax paid: £412.60
Net pay: £2,427.40

Signature: A. Okafor
```

### 7.2 Bank statement
```
BANK STATEMENT — Account 12345678
Sort Code: 12-34-56
Statement Period: 01 Jul 2026 – 31 Jul 2026

Date       Description              Amount
25 Jul 26  PELHAM CONSULTING PAY    £2,480.00
28 Jul 26  RENT PELHAM ST           -£1,200.00
30 Jul 26  SAINSBURY'S              -£84.32

Balance: £1,195.68
```

The inconsistency: payslip says net pay £2,427.40, but the deposit on the bank statement is £2,480.00 — a £52.60 difference. Gemini should catch this.

---

## 8. Regex patterns

```python
import re

REGEX_PATTERNS = {
    "ni_number":      re.compile(r'\b[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]\b'),
    "postcode":       re.compile(r'\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b'),
    "email":          re.compile(r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b'),
    "account_number": re.compile(r'\b\d{8}\b'),  # 8-digit UK account number
}
```

Note: `account_number` (8 digits) may false-positive on dates or amounts. Apply only to lines labelled "Account" or after "Bank Account:" to reduce noise. For the 2-hour build, accept some false positives — the consent step lets the user override.

---

## 9. Prompt templates

### 9.1 Gemma system prompt (local detector)
```
You are a sensitive-field detector. Find names, addresses, income amounts, and dates in the text below. Return ONLY a JSON array. No explanation, no markdown.

Format:
[{"text": "exact matched substring", "type": "name|address|income|date"}]

Text:
<DOCUMENT TEXT HERE>
```

Call with: `model=gemma4:e2b`, `think=false`, `num_predict=200`, `format="json"`.

### 9.2 Gemini system prompt (cloud reasoner)
```
You are a document analyst. You will receive one or more documents that have been redacted for privacy — sensitive fields are replaced with [REDACTED]. 

IMPORTANT: Reason ONLY over the visible text. Do NOT speculate about what [REDACTED] might contain. Do NOT attempt to identify anyone.

Your task: compare the documents and find any inconsistency in the financial figures, dates, or other factual claims. If you find one, explain it clearly and draft a short letter the user could send to resolve it.

Return JSON:
{
  "inconsistency_detected": true/false,
  "analysis": "plain language explanation of what you found",
  "draft_letter": "a draft letter if an inconsistency was found, empty string otherwise"
}

Documents:
<SANITISED PAYLOAD HERE>
```

---

## 10. Out of scope

- Guaranteed anonymisation / formal privacy guarantees.
- Real personal data.
- PDF parsing / OCR (file upload is not supported; documents are synthetic text).
- Live screen capture as input.
- Mobile or non-macOS local runtime.
- Model fine-tuning.
- Gemini tool use / function calling (cut — too much failure surface for zero demo value).
- Per-span consent overrides (per-type only).
- Server-side vault persistence (vault runs in localStorage for the demo; REST endpoints are specified in [ui.md](ui.md) §7.4 but not built).

**In scope (built by teammate, documented in [ui.md](ui.md)):**
- Vault with ACL, roles, folder lock (PBKDF2), two-step delete (TOTP).
- QR share with `#t=` instant transfer (gzip JSON) and optional AES-GCM encryption with creator key.
- Export zip (Python `build_zip_bytes`) with sanitised text, HTML, audit, and encrypted vault meta.
- Client-side redaction via `PrivacyExport` panel (browser does the redaction, not the server).

---

## Related

- [Decisions index](../decisions/index.md) — rationale for the choices above.
- [Dev log index](../dev-log/index.md) — spec review history.