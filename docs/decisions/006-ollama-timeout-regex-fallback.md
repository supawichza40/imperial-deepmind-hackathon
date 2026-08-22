# ADR-006 — 3-second Ollama timeout with regex fallback

**Date:** 22 Aug 2026
**Status:** accepted

## Context
The local model (Gemma 4 E2B) runs at 10.8 tok/s and can take 65–108s to cold-load. If Ollama hangs or is not running, the demo freezes with no recovery. Both reviewers flagged this as a mid-build failure risk.

## Decision
The Ollama call has a **3-second timeout**. If exceeded, the system falls back to regex-only detection silently and logs a warning to the audit trail.

## Consequences
- The demo cannot freeze on the local model.
- Regex-only detection catches NI numbers, postcodes, emails, and account numbers — the obvious cases. It misses names in context, which is the honest trade-off.
- The fallback is automatic; the user sees a warning in the audit log but the pipeline continues.
- The model should be kept warm before demoing, but the timeout is the safety net.

## Related
- [Spec NFR-5](../specs/privacy-gate.md)
- [notes/MEASURED-on-device-reality.md](../../notes/MEASURED-on-device-reality.md)