# ADR-012 — 3-state consent model (keep / blacklabel / encrypt)

**Date:** 22 Aug 2026
**Status:** accepted
**Supersedes:** the binary shared/blocked consent model in privacy-gate.md §3.3

## Context
The original spec used a binary consent model: `shared_types` / `blocked_types`. The built UI (PrivacyExport panel) uses a 3-state toggle per field type:

- `keep` — field stays visible (equivalent to "shared")
- `blacklabel` — field replaced with `█` bars (equivalent to "blocked", but visually distinct)
- `encrypt` — field replaced with `[ENCRYPTED ...]` using AES-GCM with a user passphrase

The binary model cannot represent encryption, which is a real capability in the built code. The 3-state model is a strict superset.

## Decision
Replace `ConsentDecision = {shared_types, blocked_types}` with:

```python
ConsentAction = Literal["keep", "blacklabel", "encrypt"]
ConsentDecision = {toggles: dict[str, ConsentAction], passphrase: str | None}
```

- `passphrase` is required when any toggle is `encrypt`. Never logged or stored.
- For backward compatibility with audit logic: `keep` → `shared`, `blacklabel`/`encrypt` → `kept_local`.

## Consequences
- API `ConsentRequest` Pydantic model changes.
- Tests that assert `shared_types`/`blocked_types` must be rewritten.
- Audit entries still use `kept_local`/`shared` (the consent decision, not the treatment).
- The `[REDACTED]` token is replaced by `█` (blacklabel) and `[ENCRYPTED ...]` (encrypt).

## Related
- [UI spec §6.3, §6.6](../specs/ui.md) — toggle values and consent object
- [redact.py](../../app/export/redact.py) — implementation