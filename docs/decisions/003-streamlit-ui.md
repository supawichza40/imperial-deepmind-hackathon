# ADR-003 — Streamlit for the consent UI

**Date:** 22 Aug 2026
**Status:** accepted

## Context
The spec did not name a UI framework. For parallel agent work, two agents building different parts could end up with incompatible stacks (one builds Streamlit, another builds FastAPI + React). Gemini's review flagged this as a P0 blocker.

## Decision
Use **Streamlit**. No debate, no alternatives.

## Consequences
- Checkboxes for per-field-type consent are trivial in Streamlit.
- Text areas for document display and sanitised payload display are built-in.
- Single-file app, no frontend/backend split needed.
- Fastest path for a 2-hour demo UI.

## Related
- [Spec §1](../specs/privacy-gate.md)