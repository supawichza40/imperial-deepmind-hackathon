# Health & Body — candidate ideas

Domain: health and body (medication timing/refills, symptoms, sleep, exercise, food/nutrition,
hydration, posture, appointments/paperwork, pain tracking, hangovers, stress). Hard rule applied:
every idea below is logistics, memory, translation, or observation only — none diagnoses or
recommends treatment.

Process: drafted 8 candidates, ran a prior-art hunter (Devpost/GitHub/Product Hunt/App
Store/Play Store) and a feasibility prover (read `starter/`, `docs/03-gemini-3.7-flash.md`,
`docs/05-gemma-4-on-device.md`, `docs/07-setup-keys-quotas-cost.md`) against all 8 in parallel.
**Fridge/Pantry Expiry Scanner** was killed outright — [PhotoFridge](https://www.photofridge.app/)
already ships the identical Gemini-powered fridge-photo-to-shopping-list flow. **Menu/Grocery
Allergy Cross-Check** was killed — [Happy Munch](https://happy-munch.com/),
[Allergy Lens](https://play.google.com/store/apps/details?id=com.emisa.allergylens), and
[SafeEat](https://safeeat.app/) already saturate this exact category. **Posture/Break Observer
(on-device)** was killed — [SitApp](https://sitapp.app/) already ships 100%-local webcam posture
detection with weekly reports and break nudges; swapping the backend to Gemma 4 isn't a delta a
judge can see. The 5 below are what survived both filters.

---

```
IDEA 1 — Bottle Cam
Problem in one sentence: "I have no idea if I've actually drunk enough water today, I'm just guessing."
Who and how often:            Every adult who drinks water from a bottle or cup, multiple times a day,
                               every day — this isn't a niche habit, it's the single most frequent
                               health-adjacent action anyone takes.
The 90-second wow:            Judge hands over their own water bottle at whatever fill level it's at.
                               One photo → "73% full, ~510ml left, you're at 1.3L of your 2L target,
                               700ml to go" appears in under 3 seconds. No typing, no manual log entry,
                               no smart-bottle hardware required.
Google feature named out loud: Gemini 3.7 Flash multimodal image input with structured JSON output —
                               genuine visual fill-fraction estimation from an ordinary photo, not OCR
                               and not a lookup table.
Closest existing thing:       HidrateSpark (https://hidratespark.com/) and Wottle
                               (https://apps.apple.com/us/app/wottle/id6758646796) — Delta: both need
                               either a $50+ BLE smart bottle or manual color-picker logging; nobody
                               shipped camera-based fill estimation from any ordinary bottle. Market
                               scan confirms it: "most hydration apps rely on manual logging or
                               sensor-equipped bottles."
Build in 3h:                  `13_hydration_tally.py` (Gemini call, Pydantic `FillEstimate{fraction_full,
                               estimated_ml}`) + camera-capture HTML page + local SQLite running tally,
                               reusing `utils.get_client`/`with_retry`. Deploy on Render/Fly.io for the
                               public link. Riskiest 20 min: fill-fraction consistency across
                               angle/lighting on a transparent bottle — a judge photographing the same
                               bottle twice can expose a visibly different number, so rehearse with the
                               actual demo bottle under venue-like lighting beforehand.
When the API throttles:       `utils.with_retry()` already backs off 429s. If wifi dies entirely: no
                               live vision fallback exists in the starter kit, so the running tally
                               still displays every entry logged before the outage, and one pre-cached
                               photo→JSON pair is kept ready so the golden-path demo works with zero
                               network.
Quotable number:              "Turns 'maybe two bottles?' into '1.3L logged, 700ml to go' — in 3 seconds."
Which track it fits:          productivity
Kill risk:                    A judge tests it on their own bottle under bad lighting and gets an
                               implausible number live — the single most exposed live-input moment in
                               this whole set. Mitigate with tight prompt calibration and a rehearsed
                               fallback bottle.
```

```
IDEA 2 — Symptom Ramble
Problem in one sentence: "I know something's been bothering me for a week but by the time I'm in
front of the doctor I can't remember when it started or how bad it actually got."
Who and how often:            Anyone tracking a recurring issue — headaches, back pain, a stomach
                               problem, a skin flare — logs an entry every time it happens, which for a
                               live recurring issue is several times a week, not just once before an
                               appointment.
The 90-second wow:            Judge talks into the mic for 20 seconds, rambling and unstructured
                               ("started maybe Tuesday, worse in the mornings, better after I eat,
                               today it's a 6 out of 10") — a clean dated timeline table appears
                               instantly, formatted as a one-page handout ready to bring to a GP.
Google feature named out loud: Gemini 3.7 Flash single-shot audio input via the Interactions API,
                               returning structured JSON (date, symptom, severity, duration) — needs
                               genuine semantic extraction over messy speech, not a transcript.
Closest existing thing:       Bearable (https://bearable.app/) and CareClinic
                               (https://careclinic.io/symptom-tracker/) — Delta: both require manual
                               tap-by-tap form entry for every log; nothing found does rambling
                               free-speech straight to a structured, dated timeline. Voice-first
                               unstructured input is a real, checkable gap in what's shipped.
Build in 3h:                  `10_symptom_timeline.py` (Gemini audio call, Pydantic
                               `TimelineEntry`/`Timeline`) + browser MediaRecorder capture page +
                               printable HTML render. Deploy on Render/Fly.io. Riskiest 20 min: mic
                               capture producing a Gemini-accepted audio mime type reliably across
                               browsers, plus anchoring vague relative dates ("a few days ago") to real
                               calendar dates — pass today's actual date explicitly in the prompt.
When the API throttles:       `with_retry()` covers rate limits at this low call volume. If wifi dies:
                               no on-device ASR exists in the kit, so one golden rehearsed clip's JSON
                               output is pre-cached and swapped in instantly for the live demo.
Quotable number:              "Cuts a 15-minute pre-appointment memory-scramble into a 15-second voice note."
Which track it fits:          productivity / accessibility (helps anyone who struggles with written
                               forms or structuring their own memory under time pressure)
Kill risk:                    Off-topic or joke input from a judge produces a nonsense timeline live —
                               keep the prompt tightly scoped to "structure what was said, invent
                               nothing" and test with a deliberately rambling adversarial clip beforehand.
```

```
IDEA 3 — Cabinet Sweep
Problem in one sentence: "I've got four bottles with four different sets of instructions and I'm not
going to remember which one needs food and which one needs to be four hours apart from the others."
Who and how often:            Anyone on a daily supplement or medication routine — a large share of
                               adults take at least one pill regularly — hits this every time they add
                               a new bottle or reorganize their routine, multiple times a week during
                               any period of change.
The 90-second wow:            Judge lays out 3-4 pill/supplement bottles (own or provided props) and
                               takes one photo of all of them at once. A single merged weekly schedule
                               appears instantly, with any timing conflicts ("these two need 4 hours
                               apart, both say morning") flagged in red — versus manually typing each
                               one into an app.
Google feature named out loud: Gemini 3.7 Flash multimodal image input, batched across multiple labels
                               in one request, structured JSON output per item — the schedule merge and
                               conflict flagging itself is deterministic Python, not a model claim.
Closest existing thing:       ScanMyPills (https://apps.apple.com/us/app/scanmypills-pill-reminder-log/id6754493741)
                               and Medisafe (https://apps.apple.com/us/app/medication-reminder-medisafe/id1643271752) —
                               Delta: both manage medications one at a time, added individually via
                               search or barcode, and Medisafe's conflict checks pull from an NIH/FDA
                               interaction database. This is a single-photo batch sweep of an entire
                               cabinet producing one merged schedule instantly, with conflicts derived
                               only from what's printed on the labels themselves — no drug database,
                               no per-item setup flow. Weakest delta in this set; say the "batch, not
                               per-item" line clearly if a judge pushes on it.
Build in 3h:                  `09_med_schedule.py` (Gemini call, Pydantic per-label schema) +
                               `schedule_logic.py` (pure-Python merge/conflict/refill-date math, no
                               LLM) + camera-capture HTML + thin Flask route. Deploy on Render/Fly.io.
                               Riskiest 20 min: OCR accuracy on real bottles — small curved text,
                               glare, brand vs. generic naming, wildly inconsistent "with food"
                               phrasing. Test 3-4 real bottles beforehand and keep known-good backup
                               photos.
When the API throttles:       `with_retry()` covers rate limits. If wifi dies: no offline vision path
                               exists in the kit, so a pre-cached photo→JSON pair for the exact demo
                               bottles is kept ready to swap in cold.
Quotable number:              "4 bottles, 4 confusing labels, merged into one schedule in under 10
                               seconds — instead of 10+ minutes typing each one in by hand."
Which track it fits:          productivity
Kill risk:                    A judge who has used ScanMyPills or Medisafe asks "what's actually
                               different" — have the one-sentence batch-vs-per-item answer ready before
                               they ask, and don't oversell the conflict-detection as anything beyond
                               label-text arithmetic.
```

```
IDEA 4 — Sleep Ledger, Spoken
Problem in one sentence: "I have a rough sense I'm not sleeping enough this week but I've never
actually added it up."
Who and how often:            Every adult wakes up every day — a 30-second spoken check-in each
                               morning is a genuinely daily-frequency habit, the highest-frequency claim
                               in this set.
The 90-second wow:            Judge speaks a rambling account of a made-up night ("went to bed
                               around midnight, up a couple times, woke at 7:30-ish") — a running
                               sleep-debt number and tonight's suggested target bedtime appear
                               instantly, no form, no taps.
Google feature named out loud: Gemini 3.7 Flash single-shot audio input via Interactions API → structured
                               JSON (bed time, wake time, naps); the debt ledger and bedtime suggestion
                               are pure Python arithmetic against a user-set target, run after
                               extraction.
Closest existing thing:       Sleep Ledger: Debt Tracker (https://apps.apple.com/us/app/sleep-ledger-debt-tracker/id6759897307)
                               and Sleep Debt Tracker (https://play.google.com/store/apps/details?id=com.sleepdebttracker.app) —
                               Delta: both already compute cumulative debt against a target and suggest
                               a bedtime, so the ledger logic itself is commodity. The only real
                               differentiator is voice-first input replacing manual/Health-app entry —
                               narrow, but it is the specific "new interaction paradigm" pattern the
                               event's own past winners favored.
Build in 3h:                  `15_sleep_debt.py` (Gemini audio call, Pydantic `SleepEntry`/`SleepLedger`)
                               + same audio-capture page as Idea 2, debt math in pure Python. Deploy on
                               Render/Fly.io. Riskiest 20 min: post-midnight bedtimes getting attributed
                               to the wrong calendar day from vague phrasing ("around midnight") — a
                               classic off-by-one that silently corrupts the whole ledger; write and
                               test explicit date-anchoring instructions against several sample
                               transcripts before demo day.
When the API throttles:       `with_retry()` covers rate limits. If wifi dies: extraction breaks (no
                               offline audio path in the kit), but the ledger arithmetic itself runs
                               fully offline once entries exist — cache a pre-entered week so the
                               running-total math can still be demoed live with zero network.
Quotable number:              "30 seconds of rambling about last night becomes an exact sleep-debt
                               number and tonight's target bedtime."
Which track it fits:          productivity
Kill risk:                    The underlying ledger-and-target-bedtime feature is fully commodity —
                               if the pitch leans on the math instead of the voice-first input, a judge
                               who's seen a sleep-debt app will discount it immediately. Lead every time
                               with "no forms, just talk."
```

```
IDEA 5 — Morning-After Plan
Problem in one sentence: "I know tomorrow's going to be rough, I just want reminders lined up
tonight so I don't have to think about it."
Who and how often:            Weakest frequency claim in this set — this only fires on nights someone
                               drinks, which for most "ordinary adults" is not multiple times a week.
                               Included because it survived prior-art and feasibility, but rank it last
                               and be ready to defend or drop it if the announced track doesn't reward it.
The 90-second wow:            Judge speaks a made-up account ("had a few around 9, stopped by
                               midnight") — a next-day timeline of water/food/rest reminders at
                               specific times appears instantly, phrased as scheduling, never advice.
Google feature named out loud: Gemini 3.7 Flash single-shot audio input → structured JSON of what/roughly-when
                               was drunk only. The reminder timeline itself is deliberately
                               template-generated in Python, not model-generated, specifically to keep
                               every output non-medical.
Closest existing thing:       HungRecover: BAC & Recovery App (https://apps.apple.com/us/app/hungrecover-bac-recovery/id6766139744) —
                               Delta: HungRecover requires manual drink entry and computes a Widmark BAC
                               estimate, which itself edges toward a medical calculation. This idea
                               drops BAC/medical estimation entirely and adds voice-first input instead
                               of manual logging — narrow but real, and the "no BAC, no medical claim"
                               framing is the safer story for hard filter #7.
Build in 3h:                  `16_hangover_planner.py` (Gemini audio call, Pydantic `DrinkEvent` list) +
                               same audio-capture page as Idea 2 + Python-templated reminder timeline
                               (not model-generated). Deploy on Render/Fly.io. Riskiest 20 min: highest
                               content-filter risk in this whole set — alcohol-consumption descriptions
                               plus any pacing-adviceish phrasing risk a blocked/empty response or the
                               model drifting into medical-sounding guidance despite instructions. Test
                               a realistic transcript early and keep the actual reminder schedule fully
                               templated in Python.
When the API throttles:       `with_retry()` covers rate limits. If wifi dies: extraction breaks, but
                               the templated reminder logic runs fully offline once one drink-event list
                               is cached — pre-cache one rehearsed clip's output as the demo fallback.
Quotable number:              "Turns 'a few drinks around 9' into a concrete next-day reminder
                               timeline in seconds, no manual logging."
Which track it fits:          productivity
Kill risk:                    Two compounding risks: the frequency claim is genuinely weak against
                               hard filter #2, and alcohol-related content is the single most likely
                               trigger for an unexpected safety block mid-demo. If either the track
                               announcement or a rehearsal run exposes either problem, drop this one
                               first.
```

---

## Ranking (best first)

1. **Bottle Cam** — cleanest prior-art delta found in the whole domain (no shipped camera-based
   fill estimator turned up anywhere in the scan), highest possible frequency claim, and the
   single cleanest "judge hands over their own object" wow moment in the set.
2. **Symptom Ramble** — real, citable gap (voice-first vs. every competitor's manual form entry),
   strong emotional hook, and it lines up directly with the domain's own "pain tracking" and
   "appointments and their paperwork" framing.
3. **Cabinet Sweep** — the wow moment (one photo, four bottles, instant merged schedule) is strong
   even though the underlying delta versus ScanMyPills/Medisafe is the thinnest of the three
   survivors — worth building only if the "batch not per-item" answer is rehearsed and ready.
4. **Sleep Ledger, Spoken** — the ledger math itself is fully commodity, so this only wins if the
   pitch leads hard with the voice-first interaction paradigm instead of the arithmetic.
5. **Morning-After Plan** — kept because it survived both filters, but it's the weakest entry on
   two separate hard filters at once (frequency, and a real content-filter risk around alcohol
   content) — the first one to cut if time runs short or the track announcement points elsewhere.
