# Phone life & accessibility — 5 candidate ideas

Domain: life on a phone/screen and accessibility (photos/screenshots as memory, notifications
and attention, digital clutter, dark patterns, doomscrolling, privacy, and accessibility —
low vision, deafness, dyslexia, ADHD, motor difficulty, cognitive load, aging users).

Started from 8 drafts. Two subagents ran in parallel: a prior-art hunter (web search across
Devpost/GitHub/Product Hunt/App Store/Play Store/built-in OS features) and a feasibility
prover (read `starter/`, `docs/03-gemini-3.7-flash.md`, `docs/05-gemma-4-on-device.md`,
`docs/07-setup-keys-quotas-cost.md`). The prior-art hunter killed 4 of the 8 outright:

- **Scam Screenshot Triage** — killed. Norton Genie (shipped app, millions of installs) and
  Gemma Guard (open-source project built for an actual Gemma hackathon — screenshot → OCR →
  on-device Gemma → scam verdict) both already ship this exact pitch, privacy angle included.
- **"Find That Screenshot"** — killed. At least five shipped App Store apps do natural-language
  screenshot search today (ShotSort, Phosum, VizKeeper, NoteSS, SnapBrain — the last built on
  Gemini specifically).
- **"Explain This Screen"** — killed. Both Apple (iOS 26 Visual Intelligence "Ask about this
  screen") and Google (Gemini-in-Android Circle-to-Search "ask about this screen") now ship
  this natively, system-wide, for free — strictly better than a paste-in-only version.
- **Photo Declutter Resurfacer** — killed. Slidebox has shipped the identical "keep-forever vs.
  clutter, one-tap bulk cleanup" pitch since ~2016.

That left 4 survivors from the original list. A 5th (Tab Triage) was drafted after the subagent
round closed to hit the requested count of 5 — it has **not** been independently prior-art- or
feasibility-checked and is flagged as such below; treat it as the backup pick, re-verify before
committing build time to it.

Ranked best first.

---

```
IDEA 1 — Notification Declutter Coach
Problem in one sentence: "My phone buzzes 80 times a day and I can't tell what actually mattered."
Who and how often:            Nearly every smartphone owner, multiple times daily — notification
                               volume is one of the most universal daily phone pain points there is.
The 90-second wow:            Judge screenshots their own real notification shade/lock screen live
                               and uploads it. App returns a per-app breakdown ("WhatsApp: 14 pings,
                               2 needed a reply", "Instagram: 9 pings, 0 needed action"), one clear
                               mute recommendation with reasoning, and a running noise-vs-signal score.
Google feature named out loud: Gemini 3.7 Flash multimodal image input + structured JSON output —
                               reasons about which pings needed action, which a fixed keyword/rule
                               filter structurally can't do.
Closest existing thing:       Pixel Notification Summaries / Notification Organizer (Android 16
                               QPR2, Dec 2025) — https://support.google.com/pixelphone/answer/16691280
                               — Delta: Google's version is an always-on Pixel-only system sorter into
                               generic categories; this is cross-platform (any screenshot, any OS),
                               a one-shot audit that explains WHY each app is noisy, and a running
                               signal/noise score, not just a category label.
Build in 3h:                  app.py (upload widget) + schema.py (Pydantic: apps:[{app_name,
                               ping_count, needed_action_count, recommendation, reasoning}],
                               noise_score, signal_score) + existing utils.py with_retry(). Riskiest
                               20 min: the image-in + structured-JSON round trip via the Interactions
                               API is a real, standard Gemini feature but is not demonstrated anywhere
                               in this starter kit — prove the call shape first, before building on it.
When the API throttles:       with_retry() backoff absorbs brief 429s; on sustained outage, fall back
                               to a pre-recorded screenshot+output pair from rehearsal.
Quotable number:               "34 notifications today — 12 real, 22 false alarms, muted in one tap."
Which track it fits:          accessibility / productivity (also strong for cognitive load / ADHD).
Kill risk:                    thinnest delta of the surviving four — a Pixel-owning judge may say
                               "my phone already does this." Must open by naming that feature and
                               immediately stating the cross-platform + reasoning-audit difference.
```

```
IDEA 2 — Dark Pattern X-Ray
Problem in one sentence: "I spent ten minutes hunting for the real cancel button and I still don't know if I found it."
Who and how often:            Most adults hit a manipulative UI pattern (forced continuity, hidden
                               unsubscribe, confirm-shaming, sneak-into-basket, cookie banners)
                               several times a week just from ordinary shopping, sign-ups, and
                               browsing — cookie-consent banners alone appear on most daily-visited
                               sites.
The 90-second wow:            Judge screenshots (or is handed) any live, real confusing cancel/
                               checkout/cookie-consent page and uploads it. App names the specific
                               manipulation tactic(s) at play in plain language and points to exactly
                               where to tap to get what they actually want.
Google feature named out loud: Gemini 3.7 Flash multimodal image reasoning + structured output — has
                               to both read the UI and reason about intent/manipulation, not just OCR
                               the text.
Closest existing thing:       Dark Pattern Detector (Devpost, Naive Bayes browser extension) —
                               https://devpost.com/software/dark-pattern-detector — plus academic
                               mobile-UI dark-pattern detectors — Delta: those are URL-based, live-
                               page, desktop-web-only scanners; this works on any screenshot including
                               native OS dialogs and outputs an exact "tap here" instruction, not just
                               a label.
Build in 3h:                  app.py + schema.py (List[{tactic, evidence, what_to_tap}]) + utils.py.
                               Riskiest 20 min: same unverified image-attach call shape as Idea 1.
When the API throttles:       with_retry(); sustained outage → canned screenshot+output fallback pair.
Quotable number:               "Found the real cancel button in 8 seconds instead of a 10-minute hunt."
Which track it fits:          safety / accessibility / consumer protection.
Kill risk:                    crowded category (multiple existing detectors, even if none match this
                               exact screenshot-agnostic shape) — must pitch narrowly, never claim to
                               have invented dark-pattern detection.
```

```
IDEA 3 — Doomscroll Mirror
Problem in one sentence: "I looked up an hour later and couldn't tell you why I was still scrolling."
Who and how often:            A large share of adults report losing track of time scrolling multiple
                               times a week; screen-time apps already prove this is a near-daily habit
                               for most smartphone owners, but existing tools only show minutes, never why.
The 90-second wow:            Judge screenshots their own phone's screen-time breakdown or a stretch
                               of scroll history. App returns one honest, specific one-line diagnosis
                               of the emotional/contextual pattern behind it (e.g. "you open this app
                               right after checking email — looks like an escape valve, not
                               entertainment"), not just a number.
Google feature named out loud: Gemini 3.7 Flash reasoning over a screenshot to infer behavioral
                               pattern/intent, with thinking_level: "high" for a more considered
                               answer — a task a duration-only timer structurally can't do.
Closest existing thing:       BloomScroller (Devpost hackathon project, local sentiment analysis +
                               warning popups) — https://devpost.com/software/bloomscroller — and
                               Opal/One Sec (real-time interruption) — Delta: those intervene live or
                               analyze in-app content in real time; this is retrospective, screenshot-
                               based, and gives one specific causal line instead of a popup or a timer.
Build in 3h:                  app.py + schema.py ({diagnosis, evidence}). Riskiest 20 min: shared
                               image-attach risk, plus this output is inherently unstructured/
                               subjective — no schema catches a weak answer, so prompt-quality tuning
                               (not plumbing) is the real time sink.
When the API throttles:       with_retry(); keep a deep bench of pre-canned one-liners since each
                               output is a single short sentence.
Quotable number:               "47 minutes of scrolling → one sentence that actually explains why."
Which track it fits:          accessibility (cognitive load/ADHD) / productivity / creative.
Kill risk:                    subjective output with no ground truth — a generic-sounding diagnosis
                               on stage undercuts the whole pitch; needs heavy rehearsal with real
                               seed screenshots, not improvised live input.
```

```
IDEA 4 — Plain-Language Live Simplifier
Problem in one sentence: "I can't tell what this insurance letter is actually asking me to do."
Who and how often:            Specific-group claim, stated honestly: primarily dyslexic, ADHD,
                               cognitive-load, and aging adults — not the majority of people. That
                               group hits dense official/real-world text (forms, letters, labels,
                               menus) several times a week.
The 90-second wow:            Judge points a phone camera at any dense real text (a form, a menu, a
                               warning label) or uploads a photo. App instantly returns a rewritten
                               plain-language version at a chosen reading level, read aloud, with the
                               specific hard words highlighted.
Google feature named out loud: Gemini 3.7 Flash multimodal image input + structured output for the
                               simplification/highlighting. Read-aloud is the plain browser Web
                               Speech API (device TTS), NOT Gemini — the Live API is confirmed
                               unsupported on gemini-3.7-flash, so this must be named correctly on
                               stage to avoid implying otherwise.
Closest existing thing:       Microsoft Immersive Reader (simplify/read-aloud/highlight, camera
                               capture via Lens) —
                               https://support.microsoft.com/en-us/topic/use-immersive-reader-in-microsoft-edge-72ac6331-2795-42eb-b3e8-c03503231f32
                               — plus Vite Vere, the Kaggle Gemma 3n grand-prize winner in this exact
                               cognitive-load/autonomy lane — Delta: Immersive Reader is locked to
                               Microsoft's own documents/browser, not arbitrary photographed
                               real-world text; this adds a reading-level slider over any camera
                               input. Real but the thinnest delta on this list.
Build in 3h:                  app.py (camera/file capture) + schema.py ({simplified_text,
                               reading_level, highlighted_terms}) + client-side speechSynthesis.speak().
                               Riskiest 20 min: shared image-attach risk, plus this is the only
                               candidate using a live camera photo instead of a clean screenshot —
                               angle/lighting/blur degrades OCR quality more than the others.
When the API throttles:       with_retry(); the read-aloud leg is fully offline regardless of API state.
Quotable number:               "A 2-page insurance letter understood in 15 seconds instead of 20
                               minutes of re-reading."
Which track it fits:          accessibility (explicitly named audience).
Kill risk:                    closest to an already-seen Gemma-hackathon grand-prize winner (Vite
                               Vere) — a GDM judge may say "we already gave this the top prize" unless
                               the reading-level-slider + arbitrary-camera-input delta is stated
                               explicitly and early.
```

```
IDEA 5 — Tab Triage (digital clutter coach)   [UNVERIFIED — see note below]
Problem in one sentence: "I have 40 browser tabs open and no idea which ones I still need."
Who and how often:            Most smartphone/laptop users accumulate open tabs or a cluttered
                               app-switcher multiple times a week; tab hoarding is a widely reported
                               cognitive-load and ADHD-adjacent pain point, not a niche one.
The 90-second wow:            Judge screenshots their own real tab-switcher/app-switcher grid. App
                               classifies each visible tab and returns a keep/close/bookmark call with
                               a one-line reason per tab ("abandoned recipe search from 3 weeks ago —
                               close", "boarding pass — keep").
Google feature named out loud: Gemini 3.7 Flash multimodal image reasoning over a grid of thumbnails/
                               titles + structured output — requires genuine per-tab content
                               understanding, which built-in "close tabs older than N days" heuristics
                               can't do.
Closest existing thing:       NOT independently checked — this idea was drafted after the prior-art
                               and feasibility subagents had already returned, to reach the requested
                               count of 5, and has not been web-searched against Devpost/App
                               Store/Play Store. The only known adjacent prior art is native browser/
                               OS tab management, which is purely recency-based, not content-reasoning-
                               based. Re-verify at the 12:15 briefing before committing real build time
                               — treat this as the weakest-evidenced idea on the list.
Build in 3h:                  same pattern as Ideas 1-3: app.py + schema.py ({tabs:[{title_guess,
                               category, recommendation, reason}]}) + utils.py. Riskiest 20 min: same
                               unverified image-attach call shape shared by every candidate here.
When the API throttles:       with_retry(); sustained outage → canned screenshot+output fallback pair.
Quotable number:               "40 open tabs sorted into keep/close/save in 10 seconds."
Which track it fits:          accessibility (cognitive load/ADHD) / productivity.
Kill risk:                    unverified prior art — a "smart tab manager" extension may already
                               exist and would kill this on sight. Backup pick only; do a 5-minute
                               prior-art check before locking it in.
```

---

## Ranking (best first)

1. **Notification Declutter Coach** — lowest feasibility risk of all five (single screenshot in,
   single JSON out, no camera-quality issue, no multi-image loop, per the feasibility prover),
   highest-frequency problem of the set (near-daily, near-universal), and a defensible delta
   against Google's own Pixel feature as long as the pitch opens by naming it.
2. **Dark Pattern X-Ray** — real delta, best "judge supplies live input" wow moment on the list
   (hand it any confusing page in the room), strong safety/consumer-protection framing that
   avoids the medical/legal/financial-advice trap. Held back from #1 only by a more crowded
   prior-art category.
3. **Doomscroll Mirror** — genuine narrow delta (retrospective, causal, one-line diagnosis vs.
   real-time nags or timers) and fits the day's cognitive-load/attention theme well, but the
   unstructured output makes quality control the real risk — needs the most rehearsal of the
   surviving four.
4. **Plain-Language Live Simplifier** — the strongest accessibility signal for GDM judges
   specifically (the brief's own steer), but sits closest to an actual Kaggle Gemma 3n grand-prize
   winner and to Microsoft's shipped Immersive Reader — winnable only if the reading-level-slider +
   arbitrary-camera delta is stated loudly and early, so ranked behind ideas with cleaner prior art.
5. **Tab Triage** — plausible and cheap to build (identical pattern to #1), but unverified against
   prior art under the time box. Backup pick: run a 5-minute prior-art check on it before committing,
   or swap in #4 as the accessibility-track pick if the announced track demands it.
