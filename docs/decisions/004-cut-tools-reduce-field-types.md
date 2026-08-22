# ADR-004 — Cut Gemini tool use and reduce field types

**Date:** 22 Aug 2026
**Status:** accepted

## Context
The original spec draft had 9 field types and a COULD requirement for Gemini tool use / function calling. Gemini's review flagged both as unrealistic for a 2-hour build: tool schemas and execution loops add massive failure surface for zero demo benefit, and 9 checkboxes + 9 prompt categories is too granular.

## Decision
- **Cut tool use entirely.** Moved to out-of-scope (spec §10).
- **Consolidate field types from 9 to 5:** `name`, `address`, `ni_number`, `account_number`, `income`. `date` and `email` are detected by regex but left unredacted by default. `employer_type` is cut.

## Consequences
- 5 checkboxes in the consent UI — clean and demo-friendly.
- Gemma's prompt is simpler (fewer categories to classify).
- No tool-execution loop to debug under time pressure.
- The wow moment (sanitised payload + audit log) is unaffected.

## Related
- [Spec §4 (field types)](../specs/privacy-gate.md)
- [Spec §10 (out of scope)](../specs/privacy-gate.md)