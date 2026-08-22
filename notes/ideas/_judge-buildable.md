# Buildability judge — every idea, scored against 3h20m net build time

**Real clock:** ~13:15 now. Lunch 13:30–14:30. Hacking ends 17:30 hard. That leaves **~3h
of build from 14:30**, and the brief itself wants 45min deploy/polish + 15min submission
buffer carved out of it — so the realistic build window is closer to **2h–2h15m of actual
coding** before you must be deploying. Every score below is judged against that number,
not against "a hackathon day."

## Two facts that gate almost every score

1. **No script in `starter/*.py` demonstrates an image-attach or audio-attach
   `interactions.create()` call.** Text-only structured output (`04_structured_output.py`
   pattern) is proven. Everything else — one image, two images, audio, live-mic streaming
   — is unverified in this repo and must be spiked in the first 15–20 minutes before any
   UI is built on top of it. This is the single biggest score driver below: **ideas that
   stay text-only score highest almost by default**, independent of how good the idea is.
2. **Measured on-device Gemma (this team's own M1, `notes/MEASURED-on-device-reality.md`):
   4.74 tok/s generation, 65s cold load, 287 tokens ≈ 2m9s for a two-sentence answer.**
   That's ~10x slower than the vendor estimate every idea file that predates the
   measurement assumed. E2B was still pulling at 12:18 and was **never actually
   benchmarked** — treat any idea that leans on "E2B will be faster" as an unverified hope,
   not a fact. Consequence: on-device Gemma is a **classification / one-JSON-field /
   one-sentence** demo only. Any idea whose golden path needs Gemma to *write* more than a
   short line, live, on stage, is not stage-viable as scoped.

A third, cross-cutting risk applies only to the `xmodel-fable.md` batch and a few
`xmodel-gpt.md` ideas: they bet on **in-browser Gemma via MediaPipe/LiteRT + WebGPU**
running on an *unknown judge's laptop* — a completely different, completely unverified
stack from the team's own tested Ollama pipeline. Nothing in this repo confirms that
stack works at all, let alone at what speed, on hardware you don't control. That's a
second untested spike stacked on top of the untested multimodal-call spike, for zero
proven benefit over just running the same model through the already-working
`07_local_gemma.py`/Ollama path server-side and streaming the result to a browser. Scored
accordingly.

Deploy path for every idea below is realistically **Render or Fly.io free tier** (Flask/
FastAPI, one Dockerfile or buildpack, ~10–15 min including account creation) or, for the
fully-client-side ideas, **Firebase Hosting / static Cloud Run** (faster, ~5 min, but only
if the idea truly has zero backend). Neither path is idea-specific risk — it's the same
15 minutes for everyone — so it isn't re-stated per row unless an idea's architecture
changes it materially.

**Correction applied 13:2x:** the local model is `gemma4:e2b`/`e4b` (Gemma **4**, not 3),
and E2B/E4B are natively multimodal — Text, Image, Audio (docs/05). The untested-image-call
risk above is real but is an *unverified integration step*, not an architectural block, for
anything going through **Ollama** (the team's actual tested path — `07_local_gemma.py`,
measured in `notes/MEASURED-on-device-reality.md`). Combined with three mitigations named in
that measured doc — pre-warm the model before judging, suppress the visible thinking tokens
(≈3x effective speedup), and prefer `gemma4:e2b` over the measured `e4b` — a short,
structured on-device output (a verdict, a field, a number) is stage-viable; free-form
generated prose is not. This bumped **Blind-Spot Wayfinder** and **CareThread** below from
2/2.5 to 3 (see their revised cells). It does **not** change the ~11 ideas running Gemma
**in-browser via MediaPipe/LiteRT/WebGPU** (most of `xmodel-fable.md`, plus ContextCrop,
Watchword, RelayMark in `xmodel-gpt.md`) — that's a different, still-completely-unverified
runtime from the Ollama path the measured numbers describe, on hardware (the judge's laptop)
nobody controls. Those scores are unchanged.

Score key: **5** = build it blind, nothing here has failed before. **4** = safe, one known
minor risk. **3** = GO only if the risky call shape is spiked and proven in the first 20
minutes — do not build UI first. **2** = NO-GO as the primary pick; only survives as a
stretch feature bolted onto something safer. **1** = not realistic in this window. **0** =
structurally undeployable/blocked.

---

## Money & Admin (`money-admin.md`)

| # | Idea | Score | What breaks first | Riskiest 20 min | GO/NO-GO |
|---|---|---|---|---|---|
| 1 | Deadline Priority Inbox | 3 | The 3–4-file-in-one-call multimodal shape has never been tried in this repo — worse than single-image, it's *multi*-image, so if it fails you don't know if it's the image param or the batching | Proving 4 images in one `interactions.create()` call actually attributes claims to the right source doc | GO — spike multi-image first, nothing else until it works |
| 2 | Owed Money Message Coach | 5 | Nothing structural — worst case is the 3 tone variants sounding too similar | Writing 2–3 few-shot examples so the tones read distinct, not the plumbing | GO |
| 3 | Renewal Ambush Negotiator | 5 | The "market range" number has no real source unless grounding is wired in — a scope decision, not a build risk | Deciding grounded-vs-disclaimed before writing the prompt, not after | GO |
| 4 | Statement Fee Hunter | 5 | Nothing structural | Keeping the synthetic statement obviously-clean so clustering doesn't wobble on stage | GO |
| 5 | Scam / Fake Bill Detector | 3.5 | Same untested single-image call shape as every image idea below | Getting a clean text list of red flags instead of chasing an on-image overlay (already correctly scoped out in the writeup) | GO — spike image call first |

## Health & Body (`health-body.md`)

| # | Idea | Score | What breaks first | Riskiest 20 min | GO/NO-GO |
|---|---|---|---|---|---|
| 1 | Bottle Cam | 3.5 | Fill-fraction consistency across lighting/angle on a transparent bottle — a judge re-photographing gets a visibly different number | The untested single-image call, then calibrating against the actual demo bottle under venue light | GO — spike + rehearse with the real bottle |
| 2 | Symptom Ramble | 3 | Single-shot audio attach is untested in this repo (different from the Live API skeleton in `06_*.py`) and browser mic → accepted-mime-type is its own risk | Proving one audio file round-trips through `interactions.create()` before building any UI | GO — spike audio first |
| 3 | Cabinet Sweep | 3.5 | OCR on real bottle labels (curved text, glare, brand vs. generic names) | Untested image call, then testing against 3–4 real bottles, not one clean prop | GO — spike + real props |
| 4 | Sleep Ledger, Spoken | 3 | Same untested audio call shape as #2, plus post-midnight date attribution silently corrupting the ledger | Audio spike, then explicit date-anchoring in the prompt | GO — spike audio first |
| 5 | Morning-After Plan | 2.5 | Same untested audio call, **plus** real content-filter risk — alcohol-consumption description is a plausible trigger for a blocked/empty response live on stage | Testing a realistic transcript early enough to know if the safety filter fires at all | NO-GO as a primary pick — cut first under time pressure |

## Inbox & Comms (`inbox-comms.md`)

| # | Idea | Score | What breaks first | Riskiest 20 min | GO/NO-GO |
|---|---|---|---|---|---|
| 1 | Is This Real? | 4.5 | Screenshot mode (stretch) hits the untested image call; the **text-paste golden path does not** | Wiring the local-Gemma toggle for real — the whole idea's delta dies if "private mode" is secretly still a cloud call | GO — text path first, screenshot mode only if time remains |
| 2 | Get Me A Human | 4 | Text-paste path is safe; the *live-mic* mode is, by the domain file's own admission, "the single riskiest 20 minutes across all 5 ideas in this file" | Not attempting live-mic on stage — scope to text-paste only | GO on text-paste scope; NO-GO if live-mic is the demo path |
| 3 | Voicemail Triage | 2 | No script demonstrates audio-attach; own writeup states there's no genuine offline fallback if it fails mid-demo | The audio call either works in 5 minutes or burns an hour with no way to know in advance (writeup's own words) | NO-GO as primary — needs a pre-recorded backup to be viable at all |
| 4 | Group Chat Unstick | 5 | Ambiguous "who hasn't responded" on messy real scrollback (prompt-quality, not plumbing) | Testing against 3–4 real sample chats, not one clean example | GO |
| 5 | Actually, When? | 5 | Contradictory/ambiguous real threads, same class of risk as #4 | Feeding today's actual date into the prompt so relative dates resolve | GO |

## Home, Food & Chores (`home-food.md`)

*Every idea in this file needs the same untested image call — the file's own author flags
this as the real go/no-go gate, not any single idea's specific risk. Scored accordingly;
none scores above 3.5.*

| # | Idea | Score | What breaks first | Riskiest 20 min | GO/NO-GO |
|---|---|---|---|---|---|
| 1 | Cleaning Product Matcher | 3 | **Two** images in one call — harder than the single-image baseline everyone else here uses | Proving the 2-image call, then never letting a judge freely pick the hazard-pair half live (own writeup's mitigation) | GO — spike 2-image first, hardest image variant in the file |
| 2 | Appliance Control Panel Decoder | 3.5 | Confidently-wrong icon interpretation on a panel the model hasn't effectively seen | Single-image spike, then rehearsing against 3–4 genuinely different real panels | GO — spike first |
| 3 | Laundry Pile Sorter | 3.5 | Model latching onto the most prominent garment instead of reasoning across the whole pile | Single-image spike, then testing multi-object reasoning specifically | GO — spike first |
| 4 | Bin Whisperer | 3 | Same image-call risk, **plus** real content-prep load: hand-curating 3–4 boroughs × ~20 materials accurately, fast, without hallucinating | Sourcing real council rules is its own 20 minutes, separate from the image spike | GO — spike first, budget curation time separately |
| 5 | Grocery Shelf Duplicate-Buy Preventer | 3 | Counting small, similar-looking tins in one photo — harder recognition task than the others here | Single-image spike, then testing on a genuinely cluttered shelf, not a clean prop | GO — spike first |

## Care & Relationships (`care-relationships.md`)

| # | Idea | Score | What breaks first | Riskiest 20 min | GO/NO-GO |
|---|---|---|---|---|---|
| 1 | CareThread | 3 *(revised, see correction below)* | Its own build plan already targets `gemma4:e2b` (the faster edge tier) — with thinking-tokens suppressed, a 150-token entry is closer to ~10s than the ~30s the domain file estimated off the unsuppressed e4b number, which is survivable if narrated as "watching it think locally." The real remaining risk is stacking **two** untested on-device integrations at once — image input and voice/text input in the same extraction call — not raw speed | Getting reliable JSON out of Gemma-over-Ollama at all for ONE modality first, before adding the second | GO only if descoped to a single input modality (voice-only or photo-only) for the live demo — attempting both stacked together in one call is still the real risk |
| 2 | CheckLine | 3 | No script demonstrates audio-attach at all | Spiking one audio call before any UI | GO — spike first |
| 3 | Wishline | 4.5 | Recall reads empty because nothing was seeded — a content-prep risk, not a technical one | Hand-writing 5–10 believable past mentions before the demo, not during it | GO |
| 4 | In Their Own Words | 3 | Same untested audio call as #2 | Audio spike; the retrieval-only design actually *lowers* model risk once the call works | GO — spike first |
| 5 | CueCard | 4.5 | Nothing structural — smallest technical footprint in the domain, text-only on-device | Resisting scope creep back toward video/gesture recognition (own writeup's stated risk) | GO |

## Phone Life & Accessibility (`phone-a11y.md`)

*All five share the same single-screenshot-image base risk. Screenshots are cleaner input
than real-world camera photos, so this domain's image risk is the mildest of the
image-dependent domains.*

| # | Idea | Score | What breaks first | Riskiest 20 min | GO/NO-GO |
|---|---|---|---|---|---|
| 1 | Notification Declutter Coach | 4 | Untested image call, but single screenshot = cleanest input of any image idea in the whole scan | Image spike, then confirming the JSON schema holds on a genuinely busy real notification shade | GO |
| 2 | Dark Pattern X-Ray | 4 | Same as #1 | Image spike + testing on a real messy checkout/cookie page | GO |
| 3 | Doomscroll Mirror | 4 | Output is a free-text diagnosis with no schema to catch a weak answer — a prompt-quality risk, not a plumbing one | Image spike, then rehearsing enough real seed screenshots to avoid a generic-sounding line live | GO |
| 4 | Plain-Language Live Simplifier | 3.5 | This is the one idea here using a live camera photo, not a screenshot — angle/lighting/blur degrades OCR more than the rest of the domain | Image spike, then testing on real dense text under bad lighting, not a scan | GO — spike first |
| 5 | Tab Triage | 4 | Same build shape as #1–3, but genuinely unverified prior art (drafted after the search subagent returned) | Same image spike as the rest of the domain | GO technically — do a 5-minute prior-art check before committing, per the file's own flag |

## Travel / Commute (`travel-commute.md`)

| # | Idea | Score | What breaks first | Riskiest 20 min | GO/NO-GO |
|---|---|---|---|---|---|
| 1 | Blind-Spot Wayfinder | 3 *(revised, see correction below)* | Ollama's `images=[...]` param for gemma4 is **not demonstrated anywhere** in this repo — it's being written from scratch. E2B/E4B are confirmed natively multimodal (docs/05), so this is an unverified integration step, not an architectural block. The idea already designs around the measured-speed mitigations (one-line JSON answer, pre-warmed model), so speed is not the real risk here — the untested `images=[...]` call is | Getting Ollama's image param working at all for gemma4:e2b/e4b in the first 20 minutes — a `gemini_fallback.py` quality-upgrade path exists for when wifi is up, so it isn't literally a zero-fallback design, but leaning on it undercuts the "fully offline" story | GO — spike the image param first; if it fails, this is the one idea in the set that can't quietly fall back without contradicting its own pitch |
| 2 | Which Row's Mine | 4 | Untested image+text call, but well-architected: `response_schema` locks the answer to one row, and a genuine Gemma fallback exists | Image spike, then testing against 3–4 real board photos (small/blurry text at frame edges) | GO — spike first |
| 3 | Cycling Rule Decoder | 4 | Same image-call risk, plus the accuracy of the hand-written Highway Code cheat sheet the model is grounded on | Image spike; writing an accurate cheat sheet is the real content risk, not the API call | GO — spike first |
| 4 | Missed-Parcel Slip Decoder | 4 | Same image-call risk, plus telling apart near-identical UK courier card formats | Image spike, then sourcing 3–4 real sample cards across couriers | GO — spike first |
| 5 | Carry-On Security Checker | 3.5 | Multi-object detection in one cluttered photo — harder than a single-subject shot, and the domain's own writeup flags this idea's Gemma fallback as "the honestly weakest of the five" | Image spike, then testing a deliberately messy packed bag | GO — spike first |

## Work & Learning (`work-learning.md`)

*The safest domain in the whole scan — four of five stay text-only or degrade cleanly to
text-only.*

| # | Idea | Score | What breaks first | Riskiest 20 min | GO/NO-GO |
|---|---|---|---|---|---|
| 1 | Spot the Gap | 5 | Model paraphrases instead of finding real task-mechanical gaps — a prompt-quality risk | Tuning against genuinely messy real pasted text, not a written-in-advance example | GO |
| 2 | Decision Archaeologist | 5 | Nothing structural — pure text in, structured text out, no camera/audio | Nothing beyond normal prompt iteration | GO |
| 3 | Rubber-Duck Handover | 4 | Text-paste fallback is "built in from the start," not bolted on — de-risks the mic path well | Getting browser mic capture into an accepted format; the live multi-turn follow-up loop is a genuinely new shape (not directly demoed anywhere in the starter kit) | GO — test mic capture first, but text fallback means it can't fully die |
| 4 | Jargon Cartographer | 2.5 | Untested image+text call **and**, separately, a hand-rolled interactive force-graph in raw Canvas/SVG with zero libraries — the writeup calls this "genuinely harder than the model call itself" | The graph renderer, not the API — this is a real frontend-engineering task inside a 2-hour budget | NO-GO as scoped — cut the interactive graph, ship a flat relationship list instead, or don't pick this one |
| 5 | Did I Get That Right? | 4.5 | Nothing structural — both inputs can be typed instead of spoken, so it degrades to the safest possible shape trivially | Nothing beyond normal prompt iteration on the diff logic | GO |

## X-model: Fable 5 (`xmodel-fable.md`)

*Six of eight bet on in-browser WebGPU/MediaPipe Gemma — the cross-cutting risk flagged
at the top of this doc. None of that stack is proven anywhere in this repo, on any
hardware, at any speed. Scores reflect that.*

| # | Idea | Score | What breaks first | Riskiest 20 min | GO/NO-GO |
|---|---|---|---|---|---|
| 1 | Second Look | 3 | Chaining 3–4 grounded Gemini calls per query is real latency and RPM exposure a single-call idea doesn't have | Getting one working grounded-tool-call chain within the free-tier RPM budget, not just one call | GO — but budget the chain, not just the first call |
| 2 | Doormat | 2 | In-browser Gemma multimodal load on an *unknown judge laptop* — the writeup's own top risk — stacked on top of a separate cloud enrichment path | Proving the in-browser LiteRT/WebGPU load works at all, before anything else | NO-GO as scoped — run the "on-device" half server-side via the team's actual working Ollama pipeline instead |
| 3 | Overshare Check | 2 | Same in-browser stack risk, plus bounding-box coordinates from a VLM are known-unreliable (own writeup names the fallback as region-free numbered callouts) | Same as #2 — the browser LLM load, not the prompt | NO-GO as scoped |
| 4 | Which Button | 2 | Same in-browser stack risk, this time with zero backend and zero cloud fallback at all | Same as #2 | NO-GO as scoped |
| 5 | Big Font | 4 | No in-browser LLM risk — this one uses a normal cloud Gemini multimodal call from a FastAPI backend, the safest architecture in this batch | Reliable crop-box coordinates from the screenshot (own writeup's flagged fallback: full screenshot + drawn arrow) | GO — best buildability in the fable batch by a clear margin |
| 6 | Backseat Games | 1.5 | Same in-browser stack risk, **plus** a claim that on-device Gemma does native local function calling via LiteRT/MediaPipe — an unverified capability claim, not just an unverified speed number | Nothing here fits in what's left of the budget cleanly | NO-GO |
| 7 | Three Piles | 2 | Same in-browser stack risk, two-photo flow (pile + dial), cluttered multi-object recognition on top | Same as #2 | NO-GO as scoped |
| 8 | Plain Words | 1 | A live, real-time local-inference pipeline that must "keep up with talking pace" — directly contradicted by this team's own measured 4.74 tok/s | Nothing salvages this in the time left | NO-GO |

## X-model: GPT (`xmodel-gpt.md`)

*Mixed bag: three reuse the team's actual working patterns closely (structured output,
tool-calling with a real arithmetic tool, one real free API call); the rest ask for either
the same in-browser stack risk as the Fable batch, or genuinely hard continuous-vision
engineering (frame tracking, real-time semantic loops) that isn't a single API call at
all.*

| # | Idea | Score | What breaks first | Riskiest 20 min | GO/NO-GO |
|---|---|---|---|---|---|
| 1 | ContextCrop | 2 | Stacks Tesseract.js OCR **and** in-browser Gemma via LiteRT **and** Canvas mask-burning — three unfamiliar pieces at once | Any one of the three could eat the whole budget alone | NO-GO as scoped |
| 2 | PurposePairs | 4 | Untested single-image call, but otherwise the best-architected idea in this batch — reuses the starter kit's actual tool-calling loop shape almost directly, and Open-Meteo needs no key/auth | Image spike, then forcing a stable single-item answer out of a noisy inventory (own writeup's flagged risk) | GO — spike first |
| 3 | Packet Cross-Exam | 3 | **Two** images (front+back) in one call, on top of OCR + arithmetic tool-calling — the arithmetic tool itself reuses `02_tool_agent.py`'s `calculate()` pattern almost exactly, which is the safe part | Proving the 2-image call before anything else | GO — spike 2-image first |
| 4 | Watchword | 1.5 | A sustained real-time 1fps local-inference loop for frame-to-frame semantic change detection — nothing in this repo's measured numbers says anything about sustained-loop feasibility, and it's a materially different ask than one-shot classification | Nothing here fits the budget cleanly | NO-GO |
| 5 | QueueCue | 1 | This is, underneath the pitch, building a lightweight object tracker (cross-frame identity + event counting) — a real CV engineering task, not a Gemini call | The tracker, not the model call — this alone is not a 3-hour problem | NO-GO |
| 6 | RelayMark | 2.5 | In-browser Gemma stack risk again, though the scope (one image, short spatial-direction text) is narrow enough it would fit the MEASURED doc's "short answer" survivable case *if* moved server-side to Ollama instead of the browser | Same in-browser load risk as the Fable batch | NO-GO as scoped, GO if re-architected onto the team's working Ollama path |
| 7 | Handoff Pin | 3.5 | Untested single-image call, otherwise a normal FastAPI + tool-calling loop, SQLite TTL, QR — all known patterns | Image spike, then keeping the model from inventing a next-step the sender never stated (own writeup's flagged risk) | GO — spike first |
| 8 | Parcel Proofreader | 3 | Two-image structured extraction (untested compounding shape), but the diff logic itself is deterministic Python with no LLM risk | Proving the 2-image call before anything else | GO — spike 2-image first |

---

## The 8 to actually start at 14:30

Picked purely on buildability, capped at two per domain so the portfolio still spans
tracks — the idea-quality ranking each domain file already did is a separate, valid
question this table doesn't try to re-litigate.

1. **Owed Money Message Coach** (money-admin, 5) — text-only, matches the proven `04`
   pattern exactly, has a real working Gemma fallback.
2. **Spot the Gap** (work-learning, 5) — text-only, same safe shape, genuine agentic
   reasoning so it clears "used Gemini meaningfully" without a stretch.
3. **Decision Archaeologist** (work-learning, 5) — text-only, showcases the 1M-token
   context window, safest build in that domain per its own review.
4. **Group Chat Unstick** (inbox-comms, 5) — text-only, safe, good Gemma fallback.
5. **Is This Real?** (inbox-comms, 4.5) — text-paste golden path is fully safe *and* it's
   the one idea in the whole scan where the on-device story is both genuinely provable
   and genuinely low-risk (short verdict output is exactly the MEASURED doc's
   stage-viable case) — best "both keynotes, safely" pick in the set.
6. **Did I Get That Right?** (work-learning, 4.5) — degrades to text-only trivially,
   nothing structural to break.
7. **Which Row's Mine** (travel-commute, 4) — best-buildable image-input idea found:
   single image, `response_schema`-locked, clean Gemini-primary/Gemma-fallback split.
8. **Notification Declutter Coach** (phone-a11y, 4) — best-buildable image-input idea in
   accessibility: single clean screenshot (not a noisy camera photo), highest-frequency
   claim in its domain.

If the announced track needs an on-device-forward pick beyond #5, swap in **Big Font**
(xmodel-fable, 4) — it's the only idea in either cross-model file that avoids the unproven
in-browser stack entirely.

Everything scored 2 or below above should not be started at 14:30 as a primary pick under
any track announcement — that's roughly a third of the full list, concentrated almost
entirely in the in-browser-LLM and continuous-vision ideas.
