# ADR-011 — Expand to 9 identity field types; supersede ADR-004

**Date:** 22 Aug 2026
**Status:** accepted
**Supersedes:** ADR-004 (cut Gemini tool use and reduce field types to 5)

## Context
ADR-004 reduced field types from 9 to 5 for the 2-hour build, cutting `email`, `phone`, `date_of_birth`, `signature`, and `personal_image`. The built frontend (`app/export/fields.py`, `app/static/`) implemented 9 types anyway because:

1. Email, phone, DOB, signature, and personal photo are all real PII categories that users need to control independently — collapsing them loses meaningful consent granularity.
2. Income was reclassified: it is NOT a field type. Pay figures stay visible because they are untyped payload data, not identity information. This is a better model than "income is a type shared by default" — it means the Gemini mismatch check works without any toggle at all.
3. The UI panel (PrivacyExport) already renders 9 toggle rows and is tested against them.

## Decision
- **9 field types** as defined in `app/export/fields.py`: `name`, `address`, `ni_number`, `account_number`, `email`, `phone`, `date_of_birth`, `signature`, `personal_image`.
- All 9 default to `blacklabel` (blocked).
- Income/pay figures are NOT a field type. They stay visible because they are untyped.
- ADR-004's field-type reduction is superseded. ADR-004's tool-use cut remains in effect.

## Consequences
- More toggle rows in the UI (9 vs 5), but the panel handles it.
- Detector must detect all 9 types (regex for most, Gemma for name/address/DOB in context).
- `income` is removed from `FieldType` everywhere.
- Tests must assert 9 types, not 5.

## Related
- [ADR-004](004-cut-tools-reduce-field-types.md) — superseded (field types portion only)
- [UI spec §6.3](../specs/ui.md) — 9 types with defaults
- [fields.py](../../app/export/fields.py) — canonical implementation