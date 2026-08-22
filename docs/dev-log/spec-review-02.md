# Architecture + API + Testing spec review — 5 rounds (10 reviews)

**Date:** 22 Aug 2026
**Work item:** spec-review-02
**Objective:** produce build-ready architecture, API, and testing specs for the Privacy Gate web app + PWA, reviewed by Gemini and Claude across 5 rounds (10 total reviews).

## What happened

1. Drafted three specs: architecture (FastAPI + PWA frontend), API (5 REST endpoints), testing (TDD with pytest).
2. Sent to Gemini (via `agy`) and Claude (via CLI) for parallel review.
3. Each round: both reviewers responded, feedback incorporated, re-sent.
4. After round 3, both reviewers declared "build-ready". Rounds 4-5 were final confirmation.

## Issues found and fixed by round

### Round 1 (reviews 1-2): structural gaps
| # | Problem | Fix |
|---|---|---|
| 1 | Service worker at `/static/` can't intercept `/` — wrong scope | Served at root `/service-worker.js` |
| 2 | `reason()` vs 502 contradiction — should it raise or catch? | `reason()` catches and returns fallback; API returns 200 with fallback body |
| 3 | `test_e2e.py` passed full `DetectionResult` instead of extracting `.spans` | Fixed: `{doc_id: res["spans"] for ...}` |
| 4 | `conftest.py` missing `import json`, `import urllib.error` | Added imports |
| 5 | `sanitise_multi` location ambiguous — in `sanitiser.py` or `api/main.py`? | Explicitly in `sanitiser.py`, API calls it |
| 6 | `test_merge_different_type` had contradictory comment | Fixed |
| 7 | Missing tests: empty JSON, tie-breaker, unsorted spans, FR-26, fallback 200 | Added all |
| 8 | `AuditRequest.detection_results` had no default → 422 if omitted | Added `= {}` default |

### Round 2 (reviews 3-4): cleanup
| # | Problem | Fix |
|---|---|---|
| 9 | API §7 still listed `502` error code after the 200-fallback decision | Removed 502 |
| 10 | API §4 had duplicate paragraph from round 1 edit | Removed duplicate |
| 11 | API §2.3 said "calls sanitise() per doc" but architecture said "calls sanitise_multi()" | API always calls `sanitise_multi()` |
| 12 | API 400 on empty consent blocked legitimate "no sensitive fields" case | Changed: empty consent → 200 unredacted |
| 13 | `test_regex_spans_have_valid_offsets` sliced literal string not variable | Fixed to use `text` variable |
| 14 | `test_reason_never_receives_original_text` fragile param name check | Accept both `payload` and `sanitised_payload` |
| 15 | `test_full_pipeline_regex_fallback` only tested detect, not full flow | Extended to all 4 stages + audit fallback entry |

### Round 3 (reviews 5-6): final alignment
| # | Problem | Fix |
|---|---|---|
| 16 | Architecture said "calls sanitise() for single doc" but API always uses sanitise_multi() | Architecture updated: always sanitise_multi() |

Both reviewers declared **build-ready**.

### Rounds 4-5 (reviews 7-10): sign-off
Both reviewers confirmed build-ready with no remaining issues.

## Related

- [Architecture spec](../specs/architecture.md)
- [API spec](../specs/api.md)
- [Testing spec](../specs/testing.md)
- [ADR-010](../decisions/010-fastapi-pwa.md) — FastAPI + PWA decision
- [Spec review 01](spec-review-01.md) — preceding spec review
- [Design review 01](design-review-01.md) — preceding design review