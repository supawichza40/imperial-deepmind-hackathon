---
name: privacy-gate
description: Build rules for Privacy Gate, the consent-aware document agent. Use when writing any Privacy Gate code, UI copy, README, pitch or submission text. Covers the local model call shape, the product framing that carries the novelty, the safety rules around sharing, and the theme.
---

# Privacy Gate build rules

This file is the source of truth for how Privacy Gate is built and described.
Edit it here and every session picks the change up. Each rule below is here
because getting it wrong cost something real today.

## The local model

- **Use `gemma4:31b-cloud`, not a locally-pulled `gemma4:e2b`.** Decided
  22 Aug 2026 ~15:51: `gemma4:e2b` was never actually pulled on the build
  machine (`ollama list` only had `gemma4:31b-cloud` and unrelated models);
  the pull was running at ~44 min ETA, too slow for the deadline. Killed it
  and switched to Ollama's cloud tag instead. Measured: a one-word structured
  reply via the native route in 0.38s total_duration. Still called through
  the exact same local Ollama client and native `/api/generate` route below
  — Ollama proxies the `-cloud` tag to a hosted endpoint, so no code path
  changes, only the model name. The "runs on-device" framing in this file's
  "What the product actually is" section now describes the redaction/consent
  architecture, not this specific model's execution location; do not claim
  gemma4:31b-cloud never leaves the machine in write-ups or demo narration.
- Historical note (superseded): `gemma4:e2b` was measured faster than
  `gemma4:e4b` (7.5s vs 14.2s warm) earlier in the day. That comparison no
  longer applies since neither is what's in use now.
- **Call the native route, `POST /api/generate`, not the OpenAI-compatible
  `/v1`.** The `/v1` route silently ignores `think: false`, so the model
  spends its whole budget on hidden reasoning and returns an empty string.
  Observed 22 Aug 2026: 36s, `max_tokens=64`, empty content.
- **Images go as `images: [base64]`** on that same native route. Proven
  working; `starter/07_local_gemma.py` is text-only and is the wrong
  reference for the vision path.
- **Keep local output short and structured.** A label, a field, a span map,
  never prose. At roughly 10 tok/s every token is a tenth of a second on
  screen. Gemma returns matched substrings plus type, not offsets and not
  rewritten text. Python resolves character offsets (ADR-001).
- **A deterministic fallback sits under the model.** Regex for account
  numbers, postcodes, NI numbers and emails catches the obvious cases
  instantly. The model handles what regex cannot: names in context,
  free-text disclosure, medical detail.

## What the product actually is

- **Lead with per-field approval and the audit trail.** Never lead with "we
  redact locally". Local-redaction-then-cloud-answer is a published tutorial
  pattern and a shipped product category; a judge who knows that hears
  "wrapper" no matter how the architecture is drawn. The consent gate is the
  defensible part.
- **Render the inference chain, not the redaction label.** Not "account
  number redacted" but what the field would let a stranger do:

  ```
  Sort code + account number  -> set up a direct debit in your name
  Full name + date of birth   -> pass a phone-banking identity check
  Employer + salary           -> a convincing payroll-change phishing email
  ```

  Same detection work, same latency. It makes the consent decision a
  judgement about consequences rather than field names.
- **The redaction step is the whole product. The cloud step is optional.**
  Value must not depend on a Gemini call succeeding. Anything sent to Gemini
  is a thing the user may then choose to do.

## Safety, and the answers to the obvious questions

- **Never auto-publish.** Batch scanning finds and prepares documents; a
  human approves each one before anything becomes shareable. Public link
  sharing stays off behind its own deliberate switch.
- **Never claim guaranteed anonymisation.** Say "assisted redaction with your
  approval". When asked "how do you know it caught everything", the honest
  answer is that it does not, which is exactly why a human approves every
  field before it leaves.
- **Exports must outlive the app.** Every document downloads as ordinary
  files that open anywhere: sanitised HTML, plain text, `audit.json`, a zip
  from `build_zip_bytes`, and `vault.enc.json` for locked fields. Nothing
  expires, nothing phones home.
- **Seed demos with synthetic documents.** Never a real person's payslip,
  statement or passport.
- **Do not self-verify novelty.** Four of eight agents had their own top idea
  killed on prior art they believed they had checked. Whoever writes a claim
  must not be the one who clears it.

## Theme and UI copy

- **Read `app/static/theme/tokens.css` and `components.css` for every value.**
  Never eyeball a colour or round a radius to a 4/8px grid.
- Page background is mist `#f7f5f2`. Cards are paper `#ffffff` at 28px.
  Images 32px. Inputs 16px. Buttons are ink pills, 44px minimum height.
- Blacklabel is ink `#111111`. Encrypt is wood `#c4a574`. Clay `#c47b6a` is
  only ever a colour dot, never a button.
- Section headings are uppercase with 0.12em tracking. Product names stay
  mixed case. Icons are 22px at 1.5px stroke, never filled.
- **No em dashes in any user-facing copy.** Rewrite the sentence rather than
  substituting a hyphen.
- Lay sibling groups out with flex or grid plus `gap`, never margins between
  inline elements.

## Submission, due 17:30

Four artefacts, each independently checkable:

1. Public GitHub repo: README, setup instructions, **architecture diagram**,
   **MIT or Apache licence**. The diagram and the licence are the two most
   commonly forgotten and cost nothing.
2. Proof of model integration: code explicitly calling Gemini 3.7 Flash via
   the Google GenAI SDK, or Gemma 4 via a local runtime.
3. A 2-minute demo video on Loom or YouTube. Shoot a rough cut at 16:00, not
   17:15.
4. A write-up of 2 to 3 paragraphs: the problem, the architecture choices,
   why Gemini or Gemma specifically, and what comes next.

Rubric: 30% technical execution and model leverage, 25% innovation, 25%
real-world impact and UX, 20% presentation including demo reliability and
Q&A defence. A recorded video controls the take but does not remove live
demo risk: a top 3 to 5 gets picked to demo in person.
