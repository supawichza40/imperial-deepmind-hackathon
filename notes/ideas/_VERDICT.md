# Adversarial verdict — `docs/visual/2026-08-22-idea-portfolio.html`

Independent verifier, no stake in the work. Default label is UNSUPPORTED without proof.
Every label below carries a `file:line`, a URL I actually fetched, or output of a command I
actually ran. Written 14:0x, 22 Aug 2026.

**Headline: I ran the spike. It passes — but not on the model the page tells you to run it on.
And the page's fallback plan is novelty-dead.**

---

## 0. A claim in my brief that is NOT on the page

I was asked to attack `"Overshare Check — prior-art searches surfaced nothing on point"` as the
page's most dangerous claim. **That sentence does not appear in the file.** `grep -in
"prior.art|novelt|nothing on point"` returns only three lines, all of which say the opposite:

- `:76` "Novelty judge still running — its verdict may yet kill one of these."
- `:145` "Only take it if the novelty judge clears it."
- `:170` "Novelty judge was still running when this page was written; its verdict is not yet reflected."

Someone is quoting a version of this claim that the artefact does not make. Whoever relayed it
should re-read the file before acting on it. I verified the substance anyway — see §1.

---

## 1. Novelty claims

| # | Claim | Label | Evidence |
|---|---|---|---|
| 1.1 | "Novelty judge still running when this page was written" | **FALSE** | `notes/ideas/_judge-novelty.md` mtime **13:28**; page self-dates **13:32** (`:57`). The verdict existed 4 minutes before the page was written and was not consulted. It kills the page's fallback. |
| 1.2 | Overshare Check has clean whitespace | **FALSE** (as a whitespace claim) | [Lookr — AI Photo Privacy](https://apps.apple.com/in/app/lookr-ai-photo-privacy/id6761846110), fetched: *"Smart AI scan – detects faces, plates, signs, logos, and content-policy risks automatically"*, *"Before & after slider – see exactly what changed before you export"*. Shipping iPhone app. The novelty judge scored it **3 — "category is warm, not cold"** (`_judge-novelty.md:80`), which is correct. |
| 1.3 | Second Look "Nothing unproven" / safe fallback | **FALSE on novelty** | [Spottable](https://spottableapp.com/): AI *"scores deals 0–100… clear verdict: Good Deal, Fair Price, or Overpriced"*, *"flags red flags… suspicious pricing, manipulated photos, seller reputation, listing inconsistencies"*, *"condition scoring and condition notes"* from listing photos. [Underpriced AI](https://underpricedai.com/): *"Snap a photo – get an instant value range, profit margins"* + *"Real sold comps"* from eBay/Poshmark/Mercari. Judge: **2 — KILL** (`_judge-novelty.md:78`). |
| 1.4 | Which Button — "same local multimodal bet", implied clean | **PARTIALLY SUPPORTED** | Judge scored 4, "verified clean" (`:81`). But [Vite Vere Offline](https://www.kaggle.com/competitions/google-gemma-3n-hackathon/writeups/vite-vere-offline) — a **Gemma 3n Impact Challenge winner featured on [blog.google](https://blog.google/innovation-and-ai/technology/developers-tools/developers-changing-lives-with-gemma-3n/)** — does images → simple instructions → read aloud by local TTS, offline, on-device Gemma. Mechanism, offline claim and spoken-steps demo shape all collide. Different user group (cognitive disability). A GDM judge is *more* likely than average to know this one — it is on Google's own blog. |
| 1.5 | ContextCrop novelty 3 | **UNVERIFIED** | I did not independently check ShareGuard / Redact Photo. Not load-bearing for the recommendation. |

**On the novelty judge's own evidence:** it cited Underpriced AI for "red flags" — Underpriced AI's
own site does **not** describe red-flag or condition detection (fetched). The kill on Second Look
still stands, but on **Spottable**, not the source the judge named. Claim laundering caught, verdict
unchanged.

---

## 2. The Gemma Guard collision

**SUPPORTED.** Gemma Guard is real and does what the page says.

- [gemmaguard.org](https://gemmaguard.org/) · [github.com/GemmaGuard/gemma-guard-android](https://github.com/GemmaGuard/gemma-guard-android) ("On-device phishing protection powered by Gemma 4. No cloud. No compromises.") · [Kaggle Gemma 4 Good Hackathon writeup](https://www.kaggle.com/competitions/gemma-4-good-hackathon/writeups/new-writeup-1775994235038)
- Captures the Android screen → OCR → **Gemma 4 locally via LiteRT-LM** → phishing verdict, nothing leaves the phone.
- Built for a **Gemma hackathon**, exactly as the page states.

"Is This Real?" was **correctly** demoted. Nothing was wrongly demoted here.

Second-order finding the page misses: Gemma Guard is a *screenshot → on-device multimodal Gemma 4 →
flag-the-risky-thing* pipeline. That is structurally the same skeleton as **Overshare Check** and
**ContextCrop**. Different job (phishing vs self-doxxing), but if a judge knows Gemma Guard, the
"look, it's local and it flags things" move is not novel to them. Lead the pitch with the inference
chain, never with "it runs locally".

---

## 3. Submission requirements

| Claim | Label | Evidence |
|---|---|---|
| **No public-URL requirement** | **SUPPORTED** | `docs/10-tracks-rules-rubric.md:55-64` lists exactly four items; none is a hosted/public URL. The page's correction is right and important. |
| Repo + architecture diagram + MIT/Apache licence | **SUPPORTED** | `docs/10:57-58` |
| Proof of model integration | **SUPPORTED** | `docs/10:59-60` |
| 2-minute video, Loom/YouTube | **SUPPORTED** | `docs/10:61-62` |
| Write-up 2–3 paragraphs | **SUPPORTED** | `docs/10:63-64` |
| **"Recorded video ⇒ 4.74 tok/s and 65s cold load stop being stage-killers"** | **FALSE / overstated** | The 20% bucket is literally named **"Presentation & Live Demo"** and includes *"demo reliability"* and *"ability to defend in Q&A"* (`docs/10:12`). `docs/00-ground-truth.md:33` records *"16:00–16:30 submission ends and judging to pick top 3–5 projects for demo"* and `:37` *"judging cut to a top 3–5, then live demos"*; `docs/01-event-brief.md:28` calls the live round **possible but unconfirmed**. **If you place top 3–5 you demo live.** On-device speed risk is reduced by the video, not retired. |
| "17:30 sharp" | **SUPPORTED, with an ambiguity** | `docs/10:55` says **17:30 GMT**. The page header says **13:32 BST**. London in August is BST (UTC+1). Work to 17:30 **BST** — it is the earlier of the two readings and therefore the safe one. |

**What to do:** keep the four-artefact framing (it is correct and valuable). Delete the sentence
claiming the recorded video neutralises the speed risk. Pre-warm the model *and* rehearse a live
90-second run, because you may have to give one.

---

## 4. On-device numbers

| Claim | Label | Evidence |
|---|---|---|
| 4.74 tok/s | **SUPPORTED** | `notes/MEASURED-on-device-reality.md:16`. My own run of `gemma4:e4b` with thinking disabled: **5.18 and 5.36 tok/s** — same ballpark, slightly better with thinking off. |
| 65 s cold load | **SUPPORTED as recorded** | `notes/MEASURED-on-device-reality.md:18`. Not reproducible now — my cold `e4b` load measured **26.2 s** because the blob is in OS page cache. 65 s is a true first-load figure; do not quote it as today's number. |
| `docs/05-gemma-4-on-device.md:51` lists E2B/E4B as Text, Image, Audio | **SUPPORTED — exact** | `docs/05:51` = `\| Modalities \| Text, Image, Audio \| Text, Image, Audio \| …` |
| "~150M-parameter vision encoder" at the same cite | **SUPPORTED, wrong line** | That is `docs/05:52`, not `:51`. Trivial. |
| README `gemma4:e2b` 10.8 tok/s | **SUPPORTED** | `README.md:91`. Independently reproduced by me: **10.86** and **10.70 tok/s**. |

---

## 5. Starter kit claims

| Claim | Label | Evidence |
|---|---|---|
| `starter/07_local_gemma.py` is text-only over Ollama | **SUPPORTED** | `starter/07_local_gemma.py:35-43` — `client.chat.completions.create` with a single text message. |
| `images=[...]` demonstrated nowhere | **SUPPORTED** | `grep -rn "images\s*=" starter/` → no matches. `grep -n "image\|base64\|vision" app/pipeline.py` → no matches. Nothing in the repo makes a local image call. |
| Implied call shape | **IMPRECISE** | `07` talks to Ollama's **OpenAI-compatible** endpoint (`:22` `BASE_URL = "http://localhost:11434/v1"`), where images are `image_url` content parts, *not* `images=[...]`. The `images=[...]` array belongs to Ollama's **native** `/api/generate`. Anyone extending `07` by adding `images=[...]` will get a wrong-shape error. Use the native endpoint — see §6, which is the shape I proved. |

---

## 6. THE SPIKE — I ran it, so you don't have to

Real command, real output, this machine, just now. `ollama list` confirms `gemma4:e2b` (7.2 GB) and
`gemma4:e4b` / `gemma4:latest` (9.6 GB, same blob `c6eb396dbd59`) are pulled.

Test image: a 640×480 PNG rendered via `qlmanage` containing a fake badge (ACME CORP / JANE OKONKWO /
SENIOR ENGINEER / BADGE ID 44821), a wifi password, and a line reading "STANDUP 9AM – Q3 LAYOFFS".
281 prompt tokens. Call: `POST http://localhost:11434/api/generate` with
`{"model": …, "prompt": "List what is readable in this photo, max 4 short items.", "images": [<base64>], "stream": false, "think": false, "options": {"num_predict": 120}}`

| Model | Cold wall | Warm wall | Rate | Output |
|---|---|---|---|---|
| `gemma4:e2b` | 31.5 s (load 18.4 s) | **7.5 s** | 10.86 tok/s | 4 correct items, structured. Minor OCR slips ("ACNE", "OKONWO"). |
| `gemma4:e4b` | 50.5 s (load 26.2 s) | **14.2 s** | 5.36 tok/s | 4 correct items, structured. Better OCR — got "ACME" and "Jane Okonkwo" right. |

### The single most consequential error on the page

The page's pass condition is **"under 12 seconds, warm"** and its spike command is
`ollama run gemma4:e4b ""`. Its instruction on failure is absolute: *"Anything else is a fail —
including 'it worked but took 40 seconds'"* and *"drop it without argument."*

**`e4b` warm takes 14.2 s. It fails the page's own bar.** A team following this page exactly would
have concluded the local image path is dead, abandoned Overshare Check, and fallen back to
**Second Look — which is novelty-dead (§1.3)**. Two wrong turns from one wrong string.

**`e2b` warm takes 7.5 s and passes comfortably**, at the cost of slightly worse OCR. The repo
already knew this: `starter/07_local_gemma.py:21` sets `MODEL = "gemma4:e2b"`, `:11-12` says e4b is
"2x slower", and `README.md:91` records e2b at 10.8 tok/s / 21 s cold. The page contradicts its own
repo.

**Fix: change the spike model to `gemma4:e2b`, keep `"think": false`, cap `num_predict`.** With that
change the spike is already passed — the capability, the call shape and the speed are all proven
above. Do not spend 20 minutes of a 3-hour budget re-proving it. Start building at 14:30.

Also correct on the page and worth keeping: `docs/05:51` confirms the vision capability is real, and
pre-warming genuinely does remove the load cost (18.4 s → 1.5 s on e2b).

---

## 7. Rubric weights

**SUPPORTED, exactly as quoted.** `docs/10-tracks-rules-rubric.md:9-12`:
30% Technical Execution & Model Leverage · 25% Innovation & Originality · 25% Real-World Impact & UX ·
20% Presentation & Live Demo. *"demo reliability"* is named explicitly at `:12`. `docs/10:14-15`
supports "deep use of one feature scores above shallow use of several".

---

## 8. AI slop / unsourced numbers / assumptions dressed as fact

| Claim | Label | Note |
|---|---|---|
| "30 agents across 8 life domains and 3 models" (`:57`) | **UNSUPPORTED** | No source anywhere. There are 10 idea files + 3 judge files; the live session lists 13 named agents. "8 life domains" and "3 models" check out; **30 agents does not**. Cut the number or count them. |
| "Six survivors of 56 candidates" | **SUPPORTED** | `_judge-wow.md:32` "All 56 ideas"; `_judge-novelty.md:1` "all 56 ideas". |
| Track 2 "Softest… Fewest entries and the most failures" | **UNSUPPORTED** | A prediction about teams who have not submitted yet, printed in a table cell as fact. No entry data can exist. Label it `assumed`. |
| Track 1 "Most crowded" | **UNSUPPORTED** | Same. |
| "There is unlikely to be a printer at Imperial" | **UNSUPPORTED** | Reasonable caution, stated as fact. Ask an organiser — costs 30 seconds. |
| "most teams will discover the speed problem at 16:00" | **UNSUPPORTED** | Rhetoric, not evidence. |
| Gemma Guard | **SUPPORTED — not slop** | Real product, real URLs, correctly characterised. Credit where due. |
| Lookr, Spottable, Underpriced AI, Vite Vere | **All real** | I fetched or searched each. The novelty judge did not invent its prior art. |

No invented file paths, no invented APIs, no fabricated citations found on the page. The
verifiable facts are mostly right; the failures are **staleness** (§1.1), **one wrong model
string** (§6), and **predictions printed as facts** (§8).

---

## 9. The page is already out of date with what the team is building

Discovered while verifying, unasked but urgent:

- `notes/ideas/privacy-gate.md:1-3` — **"Privacy Gate — consent-aware document and screen agent. Track 3 (Hybrid). Status: leading candidate as of 13:30, 22 Aug 2026."**
- `app/main.py`, `app/pipeline.py` exist (13:18); `README.md` and `SUBMISSION.md` updated **13:48** — after the page was written.

The team is building **Privacy Gate on Track 3**. That is **not one of the page's six ideas** and not
its recommendation. The portfolio page is describing a decision that has already been overtaken.

Two things about Privacy Gate nobody has checked:

1. **Its core pattern is shipped and tutorial-level.** [OpenAI Privacy Filter](https://www.f22labs.com/blogs/openai-privacy-filter-how-to-detect-and-redact-pii-before-sending-data-to-llms/) is an open-weight model released specifically to detect and mask PII locally before cloud calls; [Philter AI Proxy](https://philterd.ai/blog/redact-pii-before-sending-to-an-llm/) sells exactly this; LogRocket publishes ["How to build a local AI proxy to redact PII before LLMs"](https://blog.logrocket.com/build-local-ai-proxy-redact-pii-before-llms/) as a walkthrough. Against a 25% Innovation weight that reads *"more than a generic AI wrapper"*, "local model redacts, cloud model answers" is the generic architecture. **The only defensible novelty is the per-field human approval step** — make that the demo, not the redaction.
2. `notes/ideas/privacy-gate.md:66` says **"Do not run the local model on the lead's M1"** — while the entire Track 3 story depends on running a local model. Resolve that contradiction before 14:30.

---

## Bottom line

**The central recommendation half-survives.**

- **The `if` branch is correct and now proven, not merely bet on.** Local multimodal Gemma works on
  this laptop: 7.5 s warm, structured output, `images:[…]` on `/api/generate`. Build **Overshare
  Check on Track 2**. But its novelty is **3/5, not clean** — Lookr ships detect-and-blur *with a
  before/after slider*, which is the page's own 0:50–1:00 demo beat. Do not make before/after the
  wow. The wow is the **inference chain** ("badge → your employer → your shift pattern") plus
  genuinely offline.
- **The `else` branch is dead.** Second Look is a shipped product (Spottable: photo → deal verdict,
  overpricing, red flags, condition). Replace the fallback with **Which Button** (novelty 4, but
  check Vite Vere) or **Spot the Gap** (novelty 4, verified whitespace, safest build, weakest
  visuals).
- **Fix the spike model string before anyone runs it.** `e4b` fails the page's own 12-second bar;
  `e2b` passes it. That one character pair is the difference between building the recommended idea
  and abandoning it for a dead one.
- **Do not believe the video retires live-demo risk.** Top 3–5 may demo live and the rubric names
  Live Demo and Q&A defence.
- **And check whether the team still wants any of this** — they appear to have moved to Privacy Gate
  on Track 3 forty minutes ago.
