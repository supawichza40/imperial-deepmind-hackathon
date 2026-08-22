# ADR-005 — The local–cloud split is the product

**Date:** 22 Aug 2026
**Status:** accepted

## Context
Track 3 (Hybrid) requires both a local model and a cloud model. The question is whether each model is a separate feature, or whether the relationship between them is the feature.

## Decision
The local model (Gemma 4 E2B) exists to make the cloud model (Gemini 3.7 Flash) safe to use. The boundary between them — the gate — is the product, not a side effect. Gemma is a privacy firewall, not a smaller chatbot.

## Consequences
- The submission write-up field "why you chose Gemini and/or Gemma" answers itself: the split is the product.
- The demo's pitch moment (step 4: show the sanitised payload leaving) is built around the boundary, not around either model's output.
- Redaction must happen before any cloud call — there is no "send everything" mode.
- This framing must be stated as "assisted redaction with human approval", never "guaranteed anonymisation".

## Related
- [notes/ideas/privacy-gate.md](../../notes/ideas/privacy-gate.md) — original idea write-up
- [Spec §1](../specs/privacy-gate.md)