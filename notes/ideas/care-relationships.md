# Domain: Looking after people — candidate ideas

Scout notes: 8 candidates drafted, checked against prior art (Devpost/GitHub/Product
Hunt/App Store/Play Store + Kaggle Gemma 3n Impact Challenge winners) and against a
3-hour build plan grounded in this repo's `starter/` kit and docs. Three were killed
outright on prior art (B — teen-text tone translator, shipped almost verbatim as
["Teen Text Translator"](https://teen-translate.lovable.app/); E — pet symptom/vet-visit
log, shipped by at least three apps including one, [PetLog](https://play.google.com/store/apps/details?id=jp.nooon.petlog&hl=en_US),
that already AI-summarizes trends; G — household invisible-labor balancer, shipped by
[PairCalm](https://paircalm.com/), [FairShare](https://apps.apple.com/us/app/fairshare-couples-mental-load/id6765473407)
and others with the identical mechanic). A fourth (F, a caregiver gesture-recognition
tool) sat dangerously close to a named Kaggle Gemma 3n Impact Challenge winner (the
Eva/pictogram-to-voice AAC project) *and* was not buildable as pitched — real gesture
recognition from video is not a 3-hour problem. It survives below only in a narrowed,
reframed form. The remaining five ideas are ranked below, best first.

---

```
IDEA 1 — CareThread
Problem in one sentence: "Every time one of us calls Mum, we're the only one who knows what we noticed — and by next week even we've forgotten it too."
Who and how often:            Adult siblings coordinating an aging parent's care check in and exchange updates multiple times a week (calls, texts, visits) — this is the exact "coordinating care between siblings" pattern named in the domain brief.
The 90-second wow:            Judge speaks a sentence into the mic as a family member reporting back — "Mum seemed dizzy again after lunch, and I found this on the counter" — while holding up a photo of a pill bottle. The app extracts a structured entry entirely on-device (Gemma 4, offline), appends it to a private shared timeline, and surfaces "this is the 3rd dizziness mention this week" live.
Google feature named out loud: Gemma 4 on-device for extraction — health-adjacent family data never leaves the device — plus Gemini 3.7 Flash for a separate, non-sensitive weekly digest. Both keynotes represented in one pipeline.
Closest existing thing:       CareSplit (caresplit.app) and "Caregiver: Elderly Parent Help" (App Store) — manual structured task/vitals logs with fairness dashboards. Delta: ambient voice/photo → automatic structured extraction + pattern flagging, not manual data entry.
Build in 3h:                  app.py (Flask), templates/index.html, static/recorder.js, models.py (CareEntry), gemma_extract.py (adapt starter/07_local_gemma.py, MODEL→gemma4:e2b), timeline_store.py (SQLite), pattern_flagger.py (plain-Python frequency count, no LLM), digest.py (Gemini weekly digest). Riskiest 20 min: getting reliable JSON out of Gemma 4 over Ollama's text-only chat endpoint, measured at 4.74 tok/s on this team's M1 (not the ~12 tok/s assumed going in) — a 150-token entry takes ~30s.
When the API throttles:       Timeline is 100% local SQLite, unaffected by rate limits or dead wifi. Only the optional weekly digest needs Gemini; it degrades to a plain list of logged entries if throttled.
Quotable number:              A 10-minute "let me catch you up" phone call → a 10-second glance at what's already logged.
Which track it fits:          on-device / accessibility
Kill risk:                    Gemma 4 on an M1 CPU runs at a measured 4.74 tok/s, not the faster number the team might assume — live extraction can visibly stall on stage. Pre-warm the model, keep the demo to one short voice note, and have a pre-recorded fallback take ready.
```

```
IDEA 2 — CheckLine
Problem in one sentence: "I call Mum every day and she says she's fine, but I can't tell if 'fine' is actually changing."
Who and how often:            Adult children of elderly parents living at a distance typically do a daily or near-daily check-in call — several times a week at minimum. Direct fit for the domain's "elderly parents at a distance" pattern.
The 90-second wow:            Judge, playing the family member, speaks a short check-in message into the mic. The app transcribes it via Gemini's audio input, adds it to a running multi-week local trend (pre-seeded with prior days), and visibly surfaces a "notice, don't diagnose" trend chip — e.g. "longer pauses finding words, 3rd time this week."
Google feature named out loud: Gemini 3.7 Flash audio-modality input for transcription/scoring (cloud), plus Gemma 4 on-device for the private weekly trend-digest text (keeps the sensitive analysis local, never uploaded).
Closest existing thing:       No shipped consumer app found at this exact intersection — the closest work is clinical/research voice-based cognitive-decline screening (e.g. Cog-TiPRO), which is diagnostic, not a family check-in ritual. Delta: consumer, ritual-embedded, explicitly non-diagnostic "notice a change" framing rather than a screening claim.
Build in 3h:                  app.py, templates/index.html (record/upload), transcribe_and_score.py (Gemini audio input), drift_store.py (SQLite), drift_detector.py (plain-Python trend comparison — no LLM makes the health judgment), sample_data/checkin_day1-14.wav (seeded so weeks of "drift" are demoable in a 3-hour window). Riskiest 20 min: no script in starter/ demonstrates an audio-input call at all — spike that exact call shape before building any UI around it.
When the API throttles:       Historical trend view over already-transcribed check-ins keeps working from local storage; only today's new scoring is blocked, with a visible "try again shortly" state.
Quotable number:              "She sounded fine" → a two-week trend line a family can actually see.
Which track it fits:          accessibility / on-device
Kill risk:                    Sits closest to the brief's "no medical advice" hard filter — one careless word on stage ("this detects dementia") turns a defensible tool into a disqualifying claim. The script must say "notice," never "detect" or "diagnose." Shares the unproven-audio-call engineering risk with Idea 4.
```

```
IDEA 3 — Wishline
Problem in one sentence: "My sister mentioned months ago that she wanted a French press, and now it's her birthday and I have no idea what she said."
Who and how often:            People mention things they'd like multiple times a week in ordinary conversation — with partners, siblings, parents, friends — without ever intending to make a list. Direct fit for the domain's "birthdays and gifts, remembering what someone told you."
The 90-second wow:            Judge says a sentence live, in character as a family member — "my sister said she really needs new hiking socks" — and the app tags and stores it against a name and date in real time. Judge then asks "what should I get my sister?" and the app recalls the exact stored mention with its original context, phrased naturally.
Google feature named out loud: Gemini 3.7 Flash structured output (Interactions API, response_format=Pydantic WishItem) for both capture and recall phrasing.
Closest existing thing:       WishMe, Gifties, "Gift Ideas – Family & Friends" — all require the user to deliberately open the app and add an item. Delta: passive capture of an unprompted, casual mention, not a self-authored list.
Build in 3h:                  app.py, templates/index.html, wish_capture.py (Gemini structured output, extends starter's structured-output example), wish_store.py (SQLite), recall.py (SQL filter + one Gemini call to phrase the answer). Riskiest 20 min: "capture over time" has no real time to show live in 3 hours — the team must hand-seed 5-10 believable past mentions before the demo or recall looks empty.
When the API throttles:       recall.py degrades to printing the raw stored rows (person, item, date, context) without the "phrase nicely" LLM step.
Quotable number:              "I have no idea what to get her" → an answer in one sentence.
Which track it fits:          productivity / creative
Kill risk:                    The whole wow depends on faking a realistic conversation history convincingly — that's a writing risk, not an engineering one. If the "passive capture" framing isn't stated explicitly in the pitch, a rushed judge sees a bare gift-list app.
```

```
IDEA 4 — In Their Own Words
Problem in one sentence: "I can't remember exactly how Dad used to explain that, and I'm terrified I'm going to forget his actual words."
Who and how often:            Honestly not a steady weekly habit — this is a bursty, high-intensity need during and after a loss, hit several times a week during the weeks that matter, not an ongoing routine. Stated plainly rather than stretched to fit.
The 90-second wow:            Judge asks a question in the voice of a grieving family member — "what was Grandpa's rule about lending money?" The app searches only a small set of pre-loaded real recorded quotes (never generated) and returns the actual matched quote plus its date, shown side-by-side with the answer so the judge can verify nothing was invented.
Google feature named out loud: Gemini 3.7 Flash audio input for transcription (cloud), plus a tightly-constrained model call that is only permitted to quote, never to paraphrase as if speaking for the person.
Closest existing thing:       HereAfter AI, Seance AI, "Dadbot" — all build an interactive chatbot or voice clone that simulates the dead person, a well-documented and criticized pattern. Delta: explicitly retrieval-only over verbatim real recordings, no simulation, no generated "voice" of the deceased at all — the specific design response critics of griefbots have asked for.
Build in 3h:                  app.py, templates/index.html, memory_store.py (SQLite, raw transcript + timestamp only), transcribe.py (Gemini audio input, same call shape as Idea 2), retrieval.py (plain keyword search, deliberately not semantic embeddings), answer.py (one call, system-prompted hard against fabrication, fed only matched raw quotes). Riskiest 20 min: same unproven audio-input call shape as Idea 2 — spike it first. Also: keeping the "quotes only" promise honestly checkable on stage by displaying the raw matched transcript next to the answer.
When the API throttles:       Pre-typed seed memories keep retrieval.py fully working with zero audio/API dependency; even the phrasing step degrades to printing the raw matched quote.
Quotable number:              Not a productivity number — the honest line is "it only ever shows you what they actually said, never what an AI thinks they'd say."
Which track it fits:          safety / accessibility
Kill risk:                    Highest reputational risk on this list. A judge's first-glance reaction to "grief" + "AI" + "voice" is "oh, a deadbot" — if the presenter doesn't lead with the anti-simulation, quotes-only design in the very first sentence, it inherits the backlash of the products it was built to answer. Only pitch this if the team can hold that framing under live Q&A.
```

```
IDEA 5 — CueCard
Problem in one sentence: "The regular carer knows exactly what Dad means when he does that — but I'm covering for her tonight and I have no idea."
Who and how often:            Families sharing caregiving duties for someone with dementia, aphasia, or nonverbal communication swap in a substitute or respite carer (a grandchild, a rotating sibling, a hired respite worker) multiple times a week in many caregiving households.
The 90-second wow:            Judge, playing a substitute carer, types or speaks a short description of what they're observing — "he's pointing at the cupboard and grunting after lunch." The app matches it against a small, personalized, pre-logged set of cue-meaning pairs for that specific person and surfaces the most likely meaning with a count — "usually means thirsty, logged 3 times" — fully offline.
Google feature named out loud: Gemma 4 on-device, text-only few-shot matching against a personal, private cue dictionary that never leaves the device.
Closest existing thing:       A Kaggle Gemma 3n Impact Challenge winner fine-tuned Gemma 3n to translate a nonverbal user's pictograms into their own expressive spoken output — output-facing AAC generation for the disabled person themselves. Delta: this tool is input-facing and audience-shifted — a lookup/reference tool for whoever is filling in as caregiver that day, matching an observed cue against a family-built glossary. No vision or gesture recognition, purely text-description matching.
Build in 3h:                  app.py, templates/index.html (typed/spoken cue description + logged meaning), cue_store.py (SQLite few-shot examples), cue_lookup.py (adapt starter/07_local_gemma.py, MODEL→gemma4:e2b, few-shot text matching, no fine-tuning, no video). Riskiest 20 min: resisting the temptation to scope this back up to gesture/video recognition — the whole build only fits in 3 hours if it stays text-description-only.
When the API throttles:       Fully offline once seeded — unaffected by wifi or rate limits.
Quotable number:              "I have no idea what he means" → the answer the family already taught the app, in one lookup.
Which track it fits:          on-device / accessibility
Kill risk:                    The original, more ambitious framing (recognizing gestures live from video) is not buildable in 3 hours and sits uncomfortably close to a named prior Gemma competition winner. The version that's actually feasible and defensible is narrower — say that narrower scope out loud in the pitch rather than overclaiming, or a judge who knows the Kaggle winners will call it out.
```

---

## Ranking, best first

1. **CareThread** — best balance of genuine delta, feasible 3-hour build, and a pipeline that visibly uses both keynote features (on-device extraction + cloud digest) on the exact "sibling care coordination" pattern the domain names.
2. **CheckLine** — the strongest prior-art gap of the five (nothing shipped consumer-facing at this intersection) and plays directly to Ian Ballantyne's own on-device/eldercare track record, but carries real engineering risk (unproven audio call shape in this repo) and sits closest to the no-medical-advice line — rank 2 on upside, watch the script closely.
3. **Wishline** — the safest engineering bet (pure cloud, closely follows an existing starter pattern) with a clean live "judge supplies input, twice" wow, but it doesn't touch Gemma 4 on-device at all, which is this domain's strongest honest argument — a weaker fit for the steer, not a weaker build.
4. **In Their Own Words** — genuinely novel and the only idea here designed as a direct ethical answer to an existing, documented product controversy, but the frequency claim is honestly weak and the reputational risk is real if the framing slips even once on stage.
5. **CueCard** — the weakest of the five: it only exists because the original pitch (F) had to be reframed away from both a Kaggle-winner collision and an infeasible video-recognition scope. What survives is real and buildable, but it's a smaller, humbler tool than it started as — include only if the other four are all spoken for.
