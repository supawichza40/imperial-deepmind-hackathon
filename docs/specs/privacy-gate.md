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

**UI framework:** Streamlit. No debate, no alternatives — it's the fastest path for a demo UI with checkboxes and text display.

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
- **FR-12 (MUST):** Show the document with detected spans highlighted (colour-coded by type in Streamlit).
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
    type: str       # field type label, see §4
    start: int      # zero-based char offset into source text (inclusive)
    end: int        # zero-based char offset (exclusive)
    text: str       # the matched substring, for verification
```

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
  "shared_types":  ["income", "date"],
  "blocked_types": ["name", "address", "ni_number", "account_number"]
}
```
Every detected type appears in exactly one list.

### 3.4 Sanitised payload
Source document string with every span whose type is in `blocked_types` replaced by `[REDACTED]`. Shared-type spans left intact. Replacements applied in reverse offset order. This is the only text that crosses the gate.

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
  "approved_by": "user"
}
```
One entry per field type. `decision` is `kept_local` or `shared`.

### 3.9 Function signatures (for parallel agent work)
```python
# Detector — local, pure function
def detect(text: str) -> list[Span]: ...

# Sanitiser — deterministic, pure function
def sanitise(text: str, spans: list[Span], blocked_types: list[str]) -> str: ...

# Consent — UI produces this
def get_consent(spans: list[Span]) -> ConsentDecision: ...

# Cloud reasoner — calls Gemini
def reason(payload: str) -> dict: ...

# Audit — produces the log
def build_audit(spans: list[Span], decision: ConsentDecision) -> list[AuditEntry]: ...
```

---

## 4. Field types

Consolidated to 5 types for the 2-hour build. Each has a checkbox in the consent UI.

| Type | Detected by | Example | Default consent |
|---|---|---|---|
| `name` | Gemma | "A. Okafor" | blocked |
| `address` | Gemma + regex (postcode) | "14 Pelham St, SW7 2AZ" | blocked |
| `ni_number` | regex | "QQ123456C" | blocked |
| `account_number` | regex | "12345678" | blocked |
| `income` | Gemma | "£2,840.00" | shared |

`date` and `email` are detected by regex but grouped under existing types or left unredacted by default. Keep it simple — 5 checkboxes, not 9.

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

### 7.1 Payslip
```
PAYSLIP — July 2026
Employee: A. Okafor
NI Number: QQ123456C
Address: 14 Pelham St, London SW7 2AZ
Bank Account: 12345678
Sort Code: 12-34-56

Gross Pay: £2,840.00
Tax Deducted: £412.60
Net Pay: £2,427.40

Employer: Pelham Consulting Ltd
Pay Date: 25 July 2026
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
- File upload / PDF parsing / OCR.
- Live screen capture as input.
- Mobile or non-macOS local runtime.
- Model fine-tuning.
- Gemini tool use / function calling (cut — too much failure surface for zero demo value).
- Per-span consent overrides (per-type only).

---

## Related

- [Decisions index](../decisions/index.md) — rationale for the choices above.
- [Dev log index](../dev-log/index.md) — spec review history.