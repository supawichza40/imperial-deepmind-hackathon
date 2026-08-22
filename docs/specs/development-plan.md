# Privacy Gate — Development Plan

**What this is:** feature breakdown, TDD task sequence, and team assignment for a 3-person build.
**Approach:** TDD — every feature has tests written first (from the [testing spec](testing.md)), then implementation.
**Build window:** ~2 hours, agent-driven, 3 parallel tracks.

---

## 1. Feature breakdown

Features are ordered by dependency. Each feature is small enough for one agent to complete in one TDD cycle (write tests → implement → pass).

### Phase 0 — Foundation (no tests, data/types only)

| # | Feature | Files | Depends on | Est |
|---|---|---|---|---|
| F0.1 | Shared types | `app/types.py` | nothing | 5 min |
| F0.2 | Synthetic fixtures | `app/fixtures.py` | nothing | 5 min |
| F0.3 | Test infrastructure | `app/tests/conftest.py`, `app/tests/__init__.py`, `app/__init__.py`, `app/api/__init__.py` | F0.1, F0.2 | 10 min |
| F0.4 | Project setup | `requirements.txt` update, `.env` setup | nothing | 5 min |

### Phase 1 — Core modules (TDD, parallel after Phase 0)

| # | Feature | Files | Tests | Depends on | Est |
|---|---|---|---|---|---|
| F1.1 | Regex detector | `app/detector.py` (`_detect_regex`) | `test_detector.py` §3.1 (6 tests) | F0.1 | 15 min |
| F1.2 | Gemma detector | `app/detector.py` (`_detect_gemma`) | `test_detector.py` §3.2 (8 tests) | F1.1 | 20 min |
| F1.3 | Span merge | `app/detector.py` (`_merge_spans`, `detect`) | `test_detector.py` §3.3 (7 tests) | F1.1, F1.2 | 15 min |
| F1.4 | Sanitiser | `app/sanitiser.py` | `test_sanitiser.py` (7 tests) | F0.1 | 15 min |
| F1.5 | Audit builder | `app/audit.py` | `test_audit.py` (5 tests) | F0.1 | 10 min |
| F1.6 | Cloud reasoner | `app/reasoner.py` | `test_reasoner.py` (4 tests) | F0.1, F0.4 | 15 min |

### Phase 2 — API layer (TDD, after core modules)

| # | Feature | Files | Tests | Depends on | Est |
|---|---|---|---|---|---|
| F2.1 | FastAPI app skeleton | `app/api/main.py` (static serving + `/` route) | `test_api.py` (root + manifest tests) | F0.3 | 10 min |
| F2.2 | GET /api/documents | `app/api/main.py` | `test_api.py` (documents test) | F2.1, F0.2 | 10 min |
| F2.3 | POST /api/detect | `app/api/main.py` | `test_api.py` (detect tests) | F2.1, F1.3 | 15 min |
| F2.4 | POST /api/sanitise | `app/api/main.py` | `test_api.py` (sanitise tests) | F2.1, F1.4 | 10 min |
| F2.5 | POST /api/reason | `app/api/main.py` | `test_api.py` (reason tests) | F2.1, F1.6 | 10 min |
| F2.6 | POST /api/audit | `app/api/main.py` | `test_api.py` (audit tests) | F2.1, F1.5 | 10 min |

### Phase 3 — PWA frontend (parallel with Phase 2)

| # | Feature | Files | Depends on | Est |
|---|---|---|---|---|
| F3.1 | HTML skeleton + styles | `static/index.html`, `static/styles.css` | F2.1 (just needs to know routes) | 15 min |
| F3.2 | App logic + state machine | `static/app.js` | F2.2-F2.6 (API endpoints) | 25 min |
| F3.3 | PWA manifest + icons | `static/manifest.json`, `static/icons/` | F3.1 | 5 min |
| F3.4 | Service worker | `static/service-worker.js` | F3.1 | 10 min |

### Phase 4 — Integration (after Phases 2 + 3)

| # | Feature | Files | Tests | Depends on | Est |
|---|---|---|---|---|---|
| F4.1 | E2E test | `app/tests/test_e2e.py` | `test_e2e.py` (2 tests) | F2.3-F2.6 | 15 min |
| F4.2 | CLI fallback | `app/main.py` | manual smoke test | F1.3, F1.4, F1.5, F1.6 | 10 min |
| F4.3 | Demo dry run | — (manual) | manual verification | F4.1, F3.2 | 10 min |

---

## 2. Dependency graph

```
Phase 0 (Foundation)
  F0.1 types.py ─┐
  F0.2 fixtures  ─┤
  F0.4 setup ─────┤
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
      Phase 2 (API)     Phase 3 (Frontend — parallel)
      F2.1-F2.6         F3.1-F3.4
                   │
                   ▼
              Phase 4 (Integration)
              F4.1-F4.3
```

---

## 3. Team assignment (3 developers)

### Developer A — Detector (critical path)

Owns the most complex module. Starts immediately on Phase 0, then drives the detector through all three sub-features.

| Order | Feature | Est | Running total |
|---|---|---|---|
| 1 | F0.1 types.py | 5 min | 5 |
| 2 | F0.2 fixtures.py | 5 min | 10 |
| 3 | F0.3 conftest.py | 10 min | 20 |
| 4 | F1.1 regex detector (TDD) | 15 min | 35 |
| 5 | F1.2 Gemma detector (TDD) | 20 min | 55 |
| 6 | F1.3 span merge + detect() (TDD) | 15 min | 70 |
| 7 | F2.3 POST /api/detect (TDD) | 15 min | 85 |
| 8 | F4.1 e2e test (TDD) | 15 min | 100 |
| 9 | F4.3 demo dry run | 10 min | 110 |

**Why this person:** detector is the critical path — most complex, most likely to break, feeds the API. They also write the e2e test because they know the data flow best.

**TDD sequence for F1.1 (example):**
```
1. Write test_regex_finds_ni_number → run → fail (no detector.py)
2. Create detector.py with _detect_regex stub → run → fail (no match)
3. Implement regex patterns from spec §8 → run → pass
4. Write test_regex_finds_postcode_and_maps_to_address → run → fail
5. Add type mapping (postcode→address) → run → pass
6. ... continue through all 6 regex tests
```

### Developer B — Sanitiser + Audit + API layer

Owns the simpler core modules and the entire API layer. After core modules, builds the FastAPI app and all endpoints.

| Order | Feature | Est | Running total |
|---|---|---|---|
| 1 | F0.4 project setup (requirements.txt, .env) | 5 min | 5 |
| 2 | F1.4 sanitiser (TDD) | 15 min | 20 |
| 3 | F1.5 audit builder (TDD) | 10 min | 30 |
| 4 | F2.1 FastAPI skeleton + static serving (TDD) | 10 min | 40 |
| 5 | F2.2 GET /api/documents (TDD) | 10 min | 50 |
| 6 | F2.4 POST /api/sanitise (TDD) | 10 min | 60 |
| 7 | F2.5 POST /api/reason (TDD) | 10 min | 70 |
| 8 | F2.6 POST /api/audit (TDD) | 10 min | 80 |
| 9 | F4.2 CLI fallback | 10 min | 90 |
| 10 | F4.3 demo dry run (join A) | 10 min | 100 |

**Why this person:** sanitiser and audit are simple pure functions — quick TDD wins that build momentum. The API layer is mechanical once the core modules exist. This person becomes the API expert and handles all endpoint integration.

### Developer C — Reasoner + Frontend + PWA

Owns the cloud call and the entire frontend. Starts with the reasoner (uses existing starter code), then pivots to the PWA frontend which can be built against mock API responses while the API is still being built.

| Order | Feature | Est | Running total |
|---|---|---|---|
| 1 | F1.6 reasoner (TDD) | 15 min | 15 |
| 2 | F3.1 HTML skeleton + styles | 15 min | 30 |
| 3 | F3.2 app.js — state machine + API calls | 25 min | 55 |
| 4 | F3.3 PWA manifest + icons | 5 min | 60 |
| 5 | F3.4 service worker | 10 min | 70 |
| 6 | — wait for API endpoints from B — | | |
| 7 | Wire app.js to real API endpoints | 15 min | 85 |
| 8 | F4.3 demo dry run (join A+B) | 10 min | 95 |

**Why this person:** the reasoner is a thin wrapper around existing `starter/utils.py` code — quick to build. The frontend is the largest single piece of non-Python work and benefits from being built early against mock data, then wired to the real API once endpoints are ready. This person is the frontend and PWA expert.

**Frontend mock strategy:** Developer C builds `app.js` with hardcoded mock responses (matching the API spec shapes) for steps 2-3. Once Developer B has the endpoints running, C swaps `fetch('/api/detect', ...)` calls in (step 7). This unblocks C from waiting on the API.

---

## 4. Timeline (120 min budget)

```
Time   0    15   30   45   60   75   90   105  120
       │    │    │    │    │    │    │    │    │
A:     F0   F1.1 F1.2      F1.3 F2.3      F4.1 F4.3
       types→regex→gemma→merge→api/detect→e2e→demo
       │    │    │    │    │    │    │    │    │
B:     F0.4 F1.4 F1.5 F2.1 F2.2 F2.4 F2.5 F2.6 F4.2
       setup→san→aud→api→docs→san→rea→aud→cli
       │    │    │    │    │    │    │    │    │
C:     F1.6 F3.1      F3.2           F3.3 F3.4 wire
       rea→html→app.js───────→pwa→sw→wire→demo
       │    │    │    │    │    │    │    │    │
       ──────────── PHASE 0-1 ──── PHASE 2-3 ── PHASE 4
```

**Critical path:** A's detector (F1.1→F1.2→F1.3, ~50 min) → A's API detect endpoint (F2.3, 15 min) → A's e2e test (F4.1, 15 min). Total: ~80 min, leaving 40 min buffer.

**Integration point:** at ~85 min, all three developers converge for F4.3 (demo dry run). The app should be fully functional by then.

---

## 5. Test-first checklist per feature

Every feature follows this pattern. No exceptions except F0.1, F0.2 (data only).

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
| Gemma JSON output unparseable | high | detector falls back to regex-only | Already designed: 3s timeout + regex fallback + defensive JSON parsing (5-step strategy). Demo still works with regex-only. |
| Ollama not running during build | medium | Developer A can't test Gemma path | Mock fixtures in conftest.py cover all Gemma tests. Real Ollama only needed for final dry run. |
| Gemini API rate-limited (429) | medium | Reasoning step fails | `with_retry()` from starter/utils.py handles this. Fallback GeminiResult returned on exhaustion. |
| Frontend can't connect to API | low | App appears broken | Developer C builds against mocks first; real wiring is a separate step (F3.7). Same-origin, no CORS. |
| Span offsets wrong | medium | Redaction corrupts text | TDD: `test_regex_spans_have_valid_offsets` and `test_gemma_offsets_match_text` catch this immediately. |
| PWA install fails | low | Loses a demo differentiator | Manual check in F4.3. Icons are placeholder PNGs. Service worker scope is at root. |
| Time overrun | medium | Incomplete demo | Cut order: e2e test → CLI fallback → draft letter → second document. Never cut: detector, sanitiser, audit log, API. |

---

## 8. Cut priorities (if running over)

If the team is behind schedule at the 90-minute mark, cut in this order:

1. **F4.2 CLI fallback** — nice for testing but not needed for the demo.
2. **F4.1 E2E test** — manual demo covers the same flow.
3. **F3.4 Service worker** — PWA install still works without offline cache; just loses the offline claim.
4. **F1.2 Gemma detector** — fall back to regex-only detection. The demo still works; the "local model" story is told via the audit log's fallback entry.
5. **Second document (FR-3)** — drop to payslip only. Gemini checks within one document instead of across two.

**Never cut:** detector (regex), sanitiser, audit log, API, frontend, PWA manifest.

---

## 9. Git workflow

- All work on `main` branch (hackathon — no PRs).
- Each feature = one commit: `feat: <feature name>`.
- If two developers touch the same file (e.g., `detector.py` has F1.1, F1.2, F1.3 all by Developer A), commit incrementally per feature.
- `app/tests/` is shared — if two developers add test files simultaneously, coordinate via the testing spec's file mapping (each test file is owned by one developer).

| Test file | Owner |
|---|---|
| `conftest.py` | Developer A |
| `test_detector.py` | Developer A |
| `test_sanitiser.py` | Developer B |
| `test_audit.py` | Developer B |
| `test_reasoner.py` | Developer C |
| `test_api.py` | Developer B |
| `test_e2e.py` | Developer A |

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

## Related

- [Requirements spec](privacy-gate.md) — what each feature implements
- [Design doc](design.md) — module designs and algorithms
- [Architecture spec](architecture.md) — system structure
- [API spec](api.md) — endpoint contracts
- [Testing spec](testing.md) — test definitions for TDD
- [Decisions index](../decisions/index.md) — architectural rationale