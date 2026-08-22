# ADR-002 — Span merge and reverse-offset replacement

**Date:** 22 Aug 2026
**Status:** accepted

## Context
Regex and Gemma detect overlapping sensitive fields — e.g. a postcode regex matches `SW7 2AZ` inside an address that Gemma also matched as `14 Pelham St, London SW7 2AZ`. Naive string replacement by offset corrupts text: an earlier replacement shifts all subsequent offsets, producing broken `[REDACTED]` output.

Both spec reviewers flagged this as a silent data-corruption risk.

## Decision
1. **Merge overlapping spans of the same type** into one (earliest start, latest end).
2. **For overlapping spans of different types**, keep the longer span, drop the shorter.
3. **Apply replacements in reverse order** (highest `start` first) so earlier offsets remain valid.
4. If two spans share the same `start`, the one with the larger `end` wins.

## Consequences
- Sanitisation is deterministic and produces correct output regardless of detection order.
- The merge step is a pure function, easy to test.
- Some sub-fields (e.g. a postcode inside an address) are absorbed into the parent span — acceptable, since both are blocked by default.

## Related
- [Spec §3.6](../specs/privacy-gate.md)
- [ADR-001 (offsets resolved in Python)](001-gemma-returns-text-not-offsets.md)