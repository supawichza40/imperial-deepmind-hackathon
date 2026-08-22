# Privacy Gate — Development Plan

**What this is:** feature breakdown, TDD task sequence, and team assignment for a 3-person build.
**Approach:** TDD — every feature has tests written first (from the [testing spec](testing.md)), then implementation.
**Build window:** ~2 hours, agent-driven, 3 parallel tracks.
**Reviewed by:** Gemini and Claude (see [dev-log](../dev-log/spec-review-02.md)).

---

## 1. Feature breakdown

Features are ordered by dependency. Each feature is small enough for one agent to complete in one TDD cycle (write tests → implement → pass).

### Phase 0 — Foundation (no tests, data/types only)

| # | Feature | Files | Depends on | Est |
|---|---|---|---|---|
| F0.1 | Shared types | `app/types.py` | nothing | 5 min |
| F0.2 | Synthetic fixtures | `app/fixtures.py` | nothing | 5 min |
| F0.3 | Test infrastructure | `app/tests/conftest.py`, `app/tests/__init__.py`, `app/__init__.py`, `app/api/__init__.py` | F0.1, F0.2 | 15 min |
| F0.4 | Project setup | `requirements.txt` update, `.env` setup | nothing | 5 min |
| F0.5 | API contract reference | `app/api/contracts.py` — Pydantic models from API spec §6, importable by both `api/main.py` and `test_api.py` | F0.1 | 10 min |

**Why F0.5 exists:** Developer C needs exact JSON response shapes for frontend mocks on minute 1. Having the Pydantic models in a shared file means C can reference them directly instead of guessing. This prevents schema drift between frontend mocks and real API responses.

### Phase 1 — Core modules (TDD, parallel after Phase 0)

| # | Feature | Files | Tests | Depends on | Est |
|---|---|---|---|---|---|
| F1.1 | Regex detector | `app/detector.py` (`_detect_regex`) | `test_detector.py` §3.1 (6 tests) | F0.1 | 15 min |
| F1.2 | Gemma detector | `app/detector.py` (`_detect_gemma`) | `test_detector.py` §3.2 (8 tests) | F1.1 | 30 min |
| F1.3 | Span merge | `app/detector.py` (`_merge_spans`, `detect`) | `test_detector.py` §3.3 (7 tests) | F1.1, F1.2 | 15 min |
| F1.4 | Sanitiser | `app/sanitiser.py` | `test_sanitiser.py` (7 tests) | F0.1 | 15 min |
| F1.5 | Audit builder | `app/audit.py` | `test_audit.py` (5 tests) | F0.1 | 10 min |
| F1.6 | Cloud reasoner | `app/reasoner.py` | `test_reasoner.py` (4 tests) | F0.1, F0.4 | 15 min |

**Note on conftest dependency:** F1.4/F1.5/F1.6 don't depend on F0.3 (conftest). Their tests are self-contained — each test file defines its own fixtures or uses the `payslip_text`/`mock_ollama_success` fixtures which are only needed for detector tests. B and C can start Phase 1 before A finishes F0.3. Developer C starts F1.6 at T=0 using raw dicts and starter code, importing typed definitions from `types.py` once A pushes F0.1 at ~T=5.

### Phase 2 — API layer (TDD, all owned by Developer B)

| # | Feature | Files | Tests | Depends on | Est |
|---|---|---|---|---|---|
| F2.1 | FastAPI app skeleton | `app/api/main.py` (static serving + `/` route) | `test_api.py` (root + manifest tests) | F0.3, F0.5 | 10 min |
| F2.2 | GET /api/documents | `app/api/main.py` | `test_api.py` (documents test) | F2.1, F0.2 | 10 min |
| F2.3 | POST /api/detect | `app/api/main.py` | `test_api.py` (detect tests) | F2.1, F1.3 | 10 min |
| F2.4 | POST /api/sanitise | `app/api/main.py` | `test_api.py` (sanitise tests) | F2.1, F1.4 | 10 min |
| F2.5 | POST /api/reason | `app/api/main.py` | `test_api.py` (reason tests) | F2.1, F1.6 | 10 min |
| F2.6 | POST /api/audit | `app/api/main.py` | `test_api.py` (audit tests) | F2.1, F1.5 | 10 min |

**All API endpoints owned by Developer B.** Developer A delivers the `detect()` function; B wires it into the endpoint. No shared-file conflicts.

### Phase 3 — PWA frontend (parallel with Phase 2)

| # | Feature | Files | Depends on | Est |
|---|---|---|---|---|
| F3.1 | HTML skeleton + styles | `static/index.html`, `static/styles.css` | F0.5 (contract shapes) | 15 min |
| F3.2 | App logic + state machine | `static/app.js` (built against mock responses matching F0.5 contracts) | F0.5 | 30 min |
| F3.3 | PWA manifest + icons | `static/manifest.json`, `static/icons/` | F3.1 | 5 min |
| F3.4 | Service worker | `static/service-worker.js` | F3.1 | 10 min |
| F3.5 | Wire to real API | `static/app.js` (swap mocks for fetch calls) | F2.2-F2.6, F3.2 | 15 min |

### Phase 4 — Integration (after Phases 2 + 3)

| # | Feature | Files | Tests | Depends on | Est |
|---|---|---|---|---|---|
| F4.1 | E2E test | `app/tests/test_e2e.py` | `test_e2e.py` (2 tests) | F2.3-F2.6 | 15 min |
| F4.2 | Demo dry run | — (manual) | manual verification | F4.1, F3.5 | 15 min |

**CLI fallback (previously F4.2) is cut from the default plan.** It's first on the cut list and not worth building proactively. Only build if ahead of schedule.

---

## 2. Dependency graph

```
Phase 0 (Foundation)
  F0.1 types.py ─┐
  F0.2 fixtures  ─┤
  F0.4 setup ─────┤
  F0.5 contracts ─┤
  F0.3 conftest ──┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
  Phase 1 (Core modules — parallel)
  F1.1-F1.3    F1.4+F1.5    F1.6
  detector     sanitiser    reasoner
  +audit
      │            │            │
      └────────────┼────────────┘
                   ▼
      Phase 2 (API — all B)     Phase 3 (Frontend — C, parallel)
      F2.1-F2.6                 F3.1-F3.4 (mocks) → F3.5 (wire)
                   │
                   ▼
              Phase 4 (Integration)
              F4.1 e2e → F4.2 demo
```

---

## 3. Team assignment (3 developers)

### Developer A — Detector (critical path)

Owns the most complex module. Starts immediately on Phase 0, then drives the detector through all three sub-features. Delivers `detect()` to Developer B for API wiring.

| Order | Feature | Est | Running total |
|---|---|---|---|
| 1 | F0.1 types.py | 5 min | 5 |
| 2 | F0.2 fixtures.py | 5 min | 10 |
| 3 | F0.3 conftest.py | 15 min | 25 |
| 4 | F1.1 regex detector (TDD) | 15 min | 40 |
| 5 | F1.2 Gemma detector (TDD) | 30 min | 70 |
| 6 | F1.3 span merge + detect() (TDD) | 15 min | 85 |
| 7 | F4.1 e2e test (TDD) | 15 min | 100 |
| 8 | F4.2 demo dry run (join B+C) | 15 min | 115 |

**Why this person:** detector is the critical path — most complex, most likely to break. A delivers `detect()` as a pure function; B imports it into the API. A also writes the e2e test because they know the data flow best.

**TDD sequence for F1.1 (example):**
```
1. Write test_regex_finds_ni_number → run → fail (no detector.py)
2. Create detector.py with _detect_regex stub → run → fail (no match)
3. Implement regex patterns from spec §8 → run → pass
4. Write test_regex_finds_postcode_and_maps_to_address → run → fail
5. Add type mapping (postcode→address) → run → pass
6. ... continue through all 6 regex tests
```

**If F1.2 (Gemma) is behind at T=70 min:** trigger the cut. Stop F1.2, ship regex-only detection. The detector returns `DetectionResult(spans=regex_spans, fallback_triggered=True, warning="Gemma skipped — regex-only")`. The demo still works; the audit log tells the story.

### Developer B — Sanitiser + Audit + ALL API endpoints

Owns the simpler core modules and the entire API layer (no shared-file conflicts — B is the sole owner of `api/main.py`). After core modules, builds the FastAPI app and all endpoints, importing `detect()` from A's `detector.py`.

| Order | Feature | Est | Running total |
|---|---|---|---|
| 1 | F0.4 project setup (requirements.txt, .env) | 5 min | 5 |
| 2 | F0.5 API contracts (Pydantic models) | 10 min | 15 |
| 3 | F1.4 sanitiser (TDD) | 15 min | 30 |
| 4 | F1.5 audit builder (TDD) | 10 min | 40 |
| 5 | F2.1 FastAPI skeleton + static serving (TDD) | 10 min | 50 |
| 6 | F2.2 GET /api/documents (TDD) | 10 min | 60 |
| 7 | F2.4 POST /api/sanitise (TDD) | 10 min | 70 |
| 8 | F2.5 POST /api/reason (TDD) | 10 min | 80 |
| 9 | F2.6 POST /api/audit (TDD) | 10 min | 90 |
| 10 | F2.3 POST /api/detect (TDD — waits for A's detect()) | 10 min | 100 |
| 11 | F4.2 demo dry run (join A+C) | 15 min | 115 |

**Why this person:** sanitiser and audit are simple pure functions — quick TDD wins. The API layer is mechanical once the core modules exist. B owns `api/main.py` exclusively — no merge conflicts. F2.3 is done last because it depends on A's `detect()` function.

**If A's detect() is late:** B stubs it inline in `api/main.py` (e.g. a temporary regex-only `detect()` function inside the endpoint handler, or a mock in `test_api.py`). B does NOT modify A's `detector.py` — that would cause a git conflict. A delivers the real `detect()` later and B removes the stub.

### Developer C — Reasoner + Frontend + PWA

Owns the cloud call and the entire frontend. Starts with the reasoner (uses existing starter code), then pivots to the PWA frontend built against mock responses (using B's contract models from F0.5 for exact schema matching).

| Order | Feature | Est | Running total |
|---|---|---|---|
| 1 | F1.6 reasoner (TDD) | 15 min | 15 |
| 2 | F3.1 HTML skeleton + styles | 15 min | 30 |
| 3 | F3.2 app.js — state machine + mock API calls | 30 min | 60 |
| 4 | F3.3 PWA manifest + icons | 5 min | 65 |
| 5 | F3.4 service worker | 10 min | 75 |
| 6 | — buffer / help others / polish — | 10 min | 85 |
| 7 | F3.5 wire app.js to real API endpoints | 15 min | 100 |
| 8 | F4.2 demo dry run (join A+B) | 15 min | 115 |

**Why this person:** the reasoner is a thin wrapper around existing `starter/utils.py` code — quick to build. The frontend is the largest non-Python piece and benefits from being built early against mock data (using F0.5 contract shapes), then wired to the real API once B's endpoints are ready. C has a 10-min buffer at step 6 — use it to help A or B if they're behind, or to polish the UI.

**Frontend mock strategy:** Developer C builds `app.js` with hardcoded mock responses matching the Pydantic models from F0.5 (`app/api/contracts.py`). This ensures the mock shapes are identical to the real API shapes. Once B has the endpoints running, C swaps mocks for `fetch('/api/detect', ...)` calls in F3.5. Zero schema drift.

---

## 4. Timeline (120 min budget)

```
Time   0    15   30   45   60   75   90   105  120
       │    │    │    │    │    │    │    │    │
A:     F0.1-0.3    F1.1     F1.2          F1.3 F4.1 F4.2
       types→conftest→regex→gemma(30m)→merge→e2e→demo
       │    │    │    │    │    │    │    │    │
B:     F0.4 F0.5 F1.4 F1.5 F2.1 F2.2 F2.4 F2.5 F2.6 F2.3 F4.2
       setup→contracts→san→aud→api→docs→san→rea→aud→detect→demo
       │    │    │    │    │    │    │    │    │
C:     F1.6 F3.1      F3.2           F3.3 F3.4 --- F3.5 F4.2
       rea→html→app.js(30m)──→pwa→sw→buffer→wire→demo
       │    │    │    │    │    │    │    │    │
       ──── PHASE 0-1 ──── PHASE 2-3 ──── PHASE 4 ──
```

**Critical path:** A's full track: Phase 0 (F0.1→F0.3, 25 min) → detector (F1.1→F1.2→F1.3, 60 min) → F4.1 e2e test (15 min) → F4.2 demo (15 min). Total: **115 min**, leaving **~5 min buffer**. This is tight. The T=70 Gemma cut trigger (§8) is the primary safety valve — cutting F1.2 saves 30 min, giving ~35 min buffer.

**Real convergence point:** all three developers reach F4.2 (demo dry run) at ~100-115 min. C wires the frontend (F3.5) progressively as B's endpoints come online — wiring `/api/documents` at ~T=60, `/api/sanitise` at ~T=70, `/api/reason` at ~T=80, then full end-to-end wiring at ~T=95-100. A finishes e2e at ~100 min. All three converge for the demo dry run in the final 15 min.

**Buffer is ~5 min.** This is the reality. If anything slips, use the cut priorities in §8. The T=70 Gemma decision is the most important one — if A hasn't finished F1.2 by then, cut it and ship regex-only. That single decision recovers 30 min.

---

## 5. Test-first checklist per feature

Every feature follows this pattern. No exceptions except F0.1, F0.2, F0.5 (data/types/contracts only).

```
□ 1. Read the test definition(s) from testing spec
□ 2. Write the test file(s)
□ 3. Run pytest → tests fail (module doesn't exist)
□ 4. Create the module with stubs (functions that raise NotImplementedError)
□ 5. Run pytest → tests fail (stubs don't implement logic)
□ 6. Implement the logic
□ 7. Run pytest → tests pass
□ 8. Move to next feature
```

---

## 6. Definition of done per feature

A feature is done when:
- [ ] All tests for that feature pass (`pytest app/tests/test_<module>.py -v`)
- [ ] No imports from other features that haven't been completed yet
- [ ] Code follows the spec's data contracts exactly (no ad-hoc types)
- [ ] No hardcoded values that belong in config (model names, API keys, timeouts)
- [ ] Commit with message `feat: <feature name>`

---

## 7. Risk register and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Gemma JSON output unparseable | high | detector falls back to regex-only | 3s timeout + regex fallback + 5-step defensive JSON parsing. Demo works with regex-only. |
| Ollama not running during build | medium | A can't test Gemma path | Mock fixtures in conftest.py cover all Gemma tests. Real Ollama only needed for final dry run. |
| Gemini API rate-limited (429) | medium | Reasoning step fails | `with_retry()` from starter/utils.py. Fallback GeminiResult on exhaustion. |
| Frontend/API schema drift | medium | F3.5 wiring breaks | F0.5 shared contract file. C builds mocks from the same Pydantic models B uses for the API. |
| A's detect() late → B blocked on F2.3 | medium | API detect endpoint delayed | B stubs `detect()` temporarily (regex-only). A overwrites later. No hard block. |
| Span offsets wrong | medium | Redaction corrupts text | TDD: `test_regex_spans_have_valid_offsets` and `test_gemma_offsets_match_text` catch this immediately. |
| Service worker caches stale assets | medium | PWA serves old JS during demo | Service worker is cut #1 (see §8). If kept, use cache-busting query params on static assets. |
| Time overrun | high | Incomplete demo | Cut order in §8. Trigger Gemma cut at T=70 if A is behind. |

---

## 8. Cut priorities (if running over)

If the team is behind schedule, cut in this order:

1. **F3.4 Service worker** — high risk of caching stale assets during demo, low payoff. PWA install still works without it (manifest is enough for "Add to Home Screen"). Cut first.
2. **F4.1 E2E test** — manual demo covers the same flow. 15 min saved.
3. **F1.2 Gemma detector** — trigger at T=70 if A is behind. Ship regex-only detection. The audit log's fallback entry tells the "local model" story. 30 min saved.
4. **Second document (FR-3)** — drop to payslip only. Gemini checks within one document. 10 min saved.
5. **F3.5 Wire to real API** — demo with mock data if API isn't ready. Loses the real-pipeline demo but shows the UI. Last resort.

**Never cut:** detector (regex), sanitiser, audit log, API, frontend, PWA manifest, demo dry run.

**Decision trigger:** at T=70, check if A has finished F1.2. If not, A stops and ships regex-only. At T=90, check if B has finished all endpoints. If not, C starts wiring against whatever endpoints exist. At T=100, stop all new work — polish and demo only.

---

## 9. Git workflow

- All work on `main` branch (hackathon — no PRs).
- Each feature = one commit: `feat: <feature name>`.
- **File ownership:** each file has one owner to prevent merge conflicts.

| File | Owner | Notes |
|---|---|---|
| `app/types.py` | A | Delivered first, then stable |
| `app/fixtures.py` | A | Delivered first, then stable |
| `app/detector.py` | A | F1.1-F1.3, sequential |
| `app/sanitiser.py` | B | F1.4 |
| `app/audit.py` | B | F1.5 |
| `app/reasoner.py` | C | F1.6 |
| `app/api/contracts.py` | B | F0.5, delivered early |
| `app/api/main.py` | B | F2.1-F2.6, sole owner |
| `static/*` | C | F3.1-F3.5, sole owner |
| `app/tests/conftest.py` | A | F0.3 |
| `app/tests/test_detector.py` | A | |
| `app/tests/test_sanitiser.py` | B | |
| `app/tests/test_audit.py` | B | |
| `app/tests/test_reasoner.py` | C | |
| `app/tests/test_api.py` | B | |
| `app/tests/test_e2e.py` | A | |
| `requirements.txt` | B | F0.4 |

**No file is edited by two developers simultaneously.** If B needs A's `detect()` function, B imports it — doesn't edit `detector.py`. If A is late, B creates a temporary stub in `detector.py` only if A hasn't created the file yet; otherwise B waits for A's commit.

---

## 10. Environment setup (do this before the timer starts)

```bash
# Clone and install
git clone <repo> && cd imperial-deepmind-hackathon
python3 -m venv .venv && source .venv/bin/activate
pip install -r starter/requirements.txt
pip install fastapi uvicorn[standard] httpx pytest pytest-asyncio

# API key
cp starter/.env.example .env
# Edit .env: GEMINI_API_KEY=...

# Local model (pull early — takes time)
ollama pull gemma4:e2b

# Warm the model before demo
ollama run gemma4:e2b ""

# Verify starter code works
python starter/01_hello_gemini.py
```

---

## 11. Coordination protocol

| Time | Check-in | Action |
|---|---|---|
| T=0 | Stand-up | Confirm setup done, roles clear |
| T=25 | Phase 0 done? | A: types+fixtures+conftest committed. B: setup+contracts committed. C: reasoner committed. If not, unblock. |
| T=70 | **Gemma decision point** | Is A done with F1.2? If no, trigger cut: A ships regex-only, moves to F1.3. |
| T=90 | **API check** | Are all B's endpoints done? If no, C starts wiring against whatever exists. Stop new API work. |
| T=100 | **Feature freeze** | No new features. Polish + demo only. |
| T=115 | **Demo ready** | App running on localhost:8000. Dry run complete. |
| T=120 | **Done** | |

---

## Related

- [UI spec](ui.md) — live frontend. Backend should implement against this.
- [Requirements spec](privacy-gate.md) — what each feature implements
- [Design doc](design.md) — module designs and algorithms
- [Architecture spec](architecture.md) — system structure
- [API spec](api.md) — endpoint contracts
- [Testing spec](testing.md) — test definitions for TDD
- [Decisions index](../decisions/index.md) — architectural rationale