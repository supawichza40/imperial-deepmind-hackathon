# Spec review — Gemini + Claude

**Date:** 22 Aug 2026
**Work item:** spec-review-01
**Objective:** produce a build-ready requirements spec from the visual explainer, reviewed by two external models.

## What happened

1. Drafted initial spec from `docs/visual/2026-08-22-privacy-gate.html`. Too heavy for a 2-hour agent build — rewrote lean.
2. Sent the lean spec to Claude CLI and Gemini (via `agy`) for independent review.
3. Both reviewers converged on the same critical gaps.
4. Incorporated all feedback into the final spec.

## Key problems found and fixed

| # | Problem (flagged by both) | Fix | ADR |
|---|---|---|---|
| 1 | LLMs can't compute character offsets | Gemma returns `{text, type}`, Python resolves offsets | [ADR-001](../decisions/001-gemma-returns-text-not-offsets.md) |
| 2 | No sample documents with planted inconsistency | Wrote synthetic payslip + bank statement into spec §7 | — |
| 3 | Span overlap corrupts sanitised text | Merge rule + reverse-offset replacement in spec §3.6 | [ADR-002](../decisions/002-span-merge-and-reverse-replacement.md) |
| 4 | No UI framework locked | Streamlit | [ADR-003](../decisions/003-streamlit-ui.md) |
| 5 | 9 field types too granular | Consolidated to 5 | [ADR-004](../decisions/004-cut-tools-reduce-field-types.md) |
| 6 | Ollama could hang the demo | 3s timeout + regex fallback | [ADR-006](../decisions/006-ollama-timeout-regex-fallback.md) |
| 7 | No prompt templates | Written into spec §9 | — |
| 8 | No regex patterns | Written into spec §8 | — |
| 9 | No function signatures | Added to spec §3.9 | — |
| 10 | Gemini might speculate about redacted content | Prompt says "ignore [REDACTED]" (FR-19) | — |

## Reviewer feedback (raw summary)

### Claude
- Top blocker: missing sample documents — build can't start without them.
- Offset generation from an LLM is unreliable — return substrings, resolve in code.
- Span overlap/merge rule is missing — will corrupt output.
- Need function signatures, prompt templates, regex patterns.
- Multi-document consent is undefined.
- FR-20 (tools) is unrealistic — cut it.

### Gemini
- Same offset concern — return `{text, type}`, resolve in Python.
- UI framework must be locked (recommended Streamlit).
- Need exact fixture strings with known discrepancy.
- Ollama JSON parsing errors need defensive extraction.
- Strict 3s timeout on Ollama for fallback.
- Gemini prompt must say "ignore [REDACTED]".
- Cut tool use, reduce field types from 9 to 5.
- Add TypedDict signatures and Gemini response schema.

## Verification

- Spec is self-contained: an agent can build from it without asking questions.
- All open questions resolved with MVP defaults.
- Review log removed from spec (kept here) per project-knowledge skill: specs contain current truth, not process history.

## Lessons

- Two independent reviewers converging on the same gaps is a strong signal those are real blockers, not opinions.
- The "LLMs compute offsets" assumption was the most dangerous — it would have failed silently in production, not just in review.
- Pre-writing fixtures and prompts is not over-engineering; it's the difference between agents building in parallel vs. agents blocked waiting for decisions.

## Related

- [Spec: privacy-gate.md](../specs/privacy-gate.md)
- [Decisions index](../decisions/index.md)