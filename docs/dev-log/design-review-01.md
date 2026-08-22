# Design doc review — 5 rounds (10 reviews)

**Date:** 22 Aug 2026
**Work item:** design-review-01
**Objective:** produce a build-ready design doc from the requirements spec, reviewed by Gemini and Claude across 5 rounds (10 total reviews).

## What happened

1. Drafted design doc from the spec — module decomposition, data flow, algorithms, build instructions.
2. Sent to Gemini (via `agy`) and Claude (via CLI) for parallel review.
3. Each round: both reviewers responded, feedback incorporated, re-sent.
4. After round 4, both reviewers declared "build-ready". Round 5 was final confirmation.

## Issues found and fixed by round

### Round 1 (reviews 1-2): structural gaps
| # | Problem | Fix |
|---|---|---|
| 1 | FR-10 fallback warning had no data path to audit | Added `DetectionResult` type with `fallback_triggered` + `warning` |
| 2 | Regex `postcode`/`email` vs canonical `FieldType` mismatch | Type mapping table: postcode→address, email→address, date→dropped |
| 3 | `str.find()` collision on repeated substrings ("Pelham" ×3) | Sequential search with advancing pointer (later replaced) |
| 4 | Multi-doc state shape inconsistency | Uniform `dict[str, list[Span]]` for all modes |
| 5 | Model ID hardcoded vs `DEFAULT_MODEL` constant | Use constant from `utils.py` |
| 6 | Span merge algorithm underspecified | Formal algorithm added (later replaced with two-pass) |
| 7 | JSON parsing fallback "manual extraction" undefined | 5-step concrete strategy with regex extraction |
| 8 | Streamlit HTML highlighting risky across newlines | Line-by-line approach (later replaced) |

### Round 2 (reviews 3-4): algorithm bugs
| # | Problem | Fix |
|---|---|---|
| 9 | Sequential `str.find()` breaks on out-of-order Gemma output | Best-match with claimed-interval tracking |
| 10 | Merge algorithm not transitive — leaves overlapping spans | Two-pass: same-type merge globally, then cross-type resolution |
| 11 | `reasoner.py` doesn't strip JSON code fences — Gemini always wraps in ```` ```json ``` ```` | Added fence-stripping strategy |
| 12 | `AuditEntry` has no field for warning text | Added `details: str` field |
| 13 | `build_audit` signature mismatch (flat list vs dict) | Updated to `dict[str, list[Span]]` |
| 14 | Multi-doc `DetectionResult` stored as single, not per-doc | `detection_results: dict[str, DetectionResult]` |
| 15 | Line-by-line highlighting breaks global offsets | Global reverse-offset `<mark>` insertion in `pre-wrap` div |
| 16 | Streamlit button state loss on rerun | `st.session_state.preview_shown` flag |
| 17 | `account_number` regex line restriction ambiguous | Context-aware regex with capture group |

### Round 3 (reviews 5-6): cleanup
| # | Problem | Fix |
|---|---|---|
| 18 | D-1 still said "line-by-line" after D-9 changed to global | Harmonized D-1 with D-9 |
| 19 | Sequence diagram still said "line-by-line" | Updated to "global reverse-offset" |
| 20 | `build_audit` in §7.6 and spec §3.9 still had old signature | Aligned to dict-based signature |
| 21 | Worked example had typo: `(8,4,...)` instead of `(8,14,...)` | Fixed |
| 22 | `get_consent` from spec not mentioned in design | Added note: inlined as Streamlit checkbox state |

### Round 4 (reviews 7-8): final technical check
| # | Problem | Fix |
|---|---|---|
| 23 | Regex group indexing: `account_number` has group, others don't | Added `match.span(1) if match.lastindex else match.span(0)` note |

Both reviewers declared **build-ready**.

### Round 5 (reviews 9-10): sign-off
Both reviewers confirmed build-ready with no remaining issues.

## Related

- [Design doc](../specs/design.md) — the reviewed output
- [Spec](../specs/privacy-gate.md) — what the design implements
- [Decisions index](../decisions/index.md) — architectural rationale
- [Spec review 01](spec-review-01.md) — the preceding spec review