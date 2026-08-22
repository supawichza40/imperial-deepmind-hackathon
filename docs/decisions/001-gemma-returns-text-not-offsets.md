# ADR-001 — Gemma returns matched text, not character offsets

**Date:** 22 Aug 2026
**Status:** accepted
**Supersedes:** original spec draft (FR-7 asked for offsets directly from the LLM)

## Context
The original spec draft required Gemma 4 E2B to output `{type, start, end}` spans with zero-based character offsets. Both spec reviewers (Claude and Gemini) independently flagged this as a critical gap: small local models hallucinate arithmetic offsets and cannot reliably compute character positions in text.

## Decision
Gemma returns `{text, type}` pairs — the exact matched substring and its field type. Python resolves character offsets via `str.find()` after receiving the model output. The span map (`{type, start, end, text}`) is produced in code, not by the model.

## Consequences
- The detector prompt is simpler (model finds substrings, not positions).
- Offset resolution is deterministic and testable.
- If a matched substring appears multiple times, `str.find()` resolves to the first occurrence — acceptable for the 2-hour build, documented as a known limitation.
- `text` is retained in the span for verification and display.

## Related
- [Spec §2.2 FR-6, FR-7](../specs/privacy-gate.md)
- [ADR-002 (span merge rule)](002-span-merge-and-reverse-replacement.md)