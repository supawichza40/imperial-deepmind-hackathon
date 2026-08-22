# Privacy Gate — consent-aware document and screen agent

**Track 3 (Hybrid).** Status: leading candidate as of 13:30, 22 Aug 2026.

> **Visual explainer for teammates:**
> [`docs/visual/2026-08-22-privacy-gate.html`](../../docs/visual/2026-08-22-privacy-gate.html)
> — architecture diagram, worked payslip example, build split. Open in a browser.

## One line
A local model acts as a privacy firewall: it redacts sensitive material on-device, the
user approves exactly what may leave, and only the approved subset reaches Gemini.

## The problem
People routinely need AI help with material they cannot paste into a cloud service —
bank statements, medical letters, payslips, contracts, immigration paperwork. Today the
choice is binary: hand over everything, or get no help. Most people either overshare
without understanding what they sent, or give up and do the work manually.

## How it works

**Gemma 4, on-device:**
- Detects names, addresses, account numbers, and other sensitive fields.
- Redacts them before anything leaves the machine.
- Classifies what each section contains.
- Presents the user a per-field approval decision.

**Gemini 3.7 Flash, cloud, receiving only approved content:**
- Reasons across several documents at once.
- Explains complex content in plain language.
- Produces an application checklist, compares documents, detects inconsistencies,
  drafts a response.
- Uses tools to carry out approved actions.

**The interface shows a live audit trail:**
```
Gemma removed account number
  → user approved sharing income figures
    → Gemini compared three documents
      → no private originals left the device
```

## Why it scores

| Criterion | Weight | Why this fits |
|---|---|---|
| Technical Execution & Model Leverage | 30% | A genuine local–cloud split with a real reason for the boundary. Multimodal document input, structured output for the redaction map, tool use on the cloud side. |
| Innovation & Originality | 25% | The local model is a privacy firewall, not a smaller chatbot. That is an architecture, not a wrapper. |
| Real-World Impact & UX | 25% | Healthcare, finance, legal, immigration, enterprise document handling. Named organiser interests include privacy-preserving clinical and sensitive enterprise audit tools. |
| Presentation & Live Demo | 20% | Redaction and consent decisions are visible on screen. A judge understands the value without an explanation. |

The write-up field "why you chose Gemini and/or Gemma" answers itself here, which is
rare — the split is the product, not a justification written afterwards.

## The two-minute demo

1. Drop in a bank statement, a payslip and an application form.
2. Gemma highlights sensitive fields locally, on screen.
3. User selects: *"Share income, but hide identity and account details."*
4. The sanitised version sent to Gemini is shown explicitly.
5. Gemini compares the documents and finds something useful — an inconsistent income
   figure, or missing evidence.
6. It produces a checklist and drafts the required explanation.
7. Close by opening the audit log: what stayed local, what was shared.

The magic moment is step 4 — the user sees the redacted payload leave, and sees that the
originals did not.

## Build notes and risks

- **Do not run the local model on the lead's M1.** Measured 10.8 tok/s on `gemma4:e2b`
  and it makes that machine sluggish while resident. Host the Gemma half on a teammate's
  machine, or pre-record that segment. See `notes/MEASURED-on-device-reality.md`.
- **Keep local outputs short.** Redaction should return a structured span map
  (field type + character offsets), not rewritten prose. That plays to the speed limit
  instead of fighting it.
- **A deterministic fallback belongs under the model.** Regex for account numbers,
  postcodes, NI numbers and emails catches the obvious cases instantly and makes the
  demo robust if the local model is slow or misses one. The model handles what regex
  cannot: names in context, free-text disclosure, medical detail.
- **Redaction is a claim you must not overstate.** Say "assisted redaction with human
  approval", never "guaranteed anonymisation". A judge may well probe this, and the
  honest framing is also the defensible one: the user approves every field before it
  leaves.
- **Seed the documents in advance.** Use synthetic statements and payslips, never a real
  person's. Have them loaded and ready before the demo starts.

## Scope for 4 hours

Minimum viable version that still lands the wow moment:
1. One document type (a payslip or bank statement), not three.
2. Regex + Gemma span detection producing a redaction map.
3. A consent UI: checkboxes per detected field type.
4. One Gemini task on the approved payload — the inconsistency check is the most
   demo-visible.
5. The audit log. This is cheap to build and it is the thing judges remember.

Cut before anything else: live screen capture, multi-document comparison, tool actions.
