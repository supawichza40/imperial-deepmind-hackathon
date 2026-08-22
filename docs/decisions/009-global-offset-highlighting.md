# ADR-009 — Global reverse-offset highlighting, not line-by-line

**Date:** 22 Aug 2026
**Status:** accepted
**Supersedes:** the line-by-line highlighting approach in design round 1

## Context
Round 1 proposed splitting the document into lines and wrapping span portions per line. Both reviewers flagged that spans have global character offsets — slicing `line[span.start:span.end]` would throw `IndexError` or slice the wrong text unless the agent explicitly tracks line-start cumulative offsets. This is error-prone under time pressure.

## Decision
Use the **same reverse-offset algorithm as the sanitiser**, but insert `<mark style="background-color:...">text</mark>` instead of `[REDACTED]`. Wrap in `<div style="white-space: pre-wrap; font-family: monospace;">`. Process spans in reverse offset order. Do NOT split by lines.

## Consequences
- Highlighting and redaction share the exact same algorithm — no drift between preview and redacted output.
- No line-offset bookkeeping needed.
- `unsafe_allow_html=True` in `st.markdown` is required (acceptable for a demo app with controlled input).

## Related
- [Design §3.7 step 5](../specs/design.md)
- [ADR-002 (reverse-offset replacement)](002-span-merge-and-reverse-replacement.md)