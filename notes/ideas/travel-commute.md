# Travel / commute — "Getting Around" candidate ideas

Domain: daily commute, delayed/cancelled trains, buses, driving and parking, cycling,
ticket machines and fare rules, being lost, foreign signage/menus abroad, packing,
airport/border admin, car trouble, delivery/parcel chaos, being somewhere unfamiliar.

Sourced against `docs/00-ground-truth.md`, `docs/08-judging-and-win-strategy.md` (§4/§5 —
none of these repeat the candidates already listed there), `docs/03-gemini-3.7-flash.md`,
`docs/05-gemma-4-on-device.md`, `docs/07-setup-keys-quotas-cost.md`, `notes/MEASURED-on-device-reality.md`,
and the starter kit at `starter/`.

**Process note:** started from 8 candidates. A dedicated prior-art subagent (web search across
Devpost/GitHub/App Store/Play Store) killed 3 outright — Stacked Parking-Sign Decoder (already
shipped 3x over: ParkLens, ClearPark, "Can I Park Here AI"), Ticket-Machine Whisperer (Google
Lens/Translate camera mode already names "vending machine instructions" as a use case), and
Foreign Menu Reality-Check (MenuPics/Menu Translator already bundle spice-level and portion-size
tags with translation). A feasibility subagent stalled mid-task and never returned usable output
after redirection, so feasibility below (file lists, API surface, throttle/wifi fallback, paid-API
flags) was verified directly against the docs and starter kit myself rather than through that
subagent — flagged here for honesty, not hidden. **Update:** the feasibility subagent's reply
did eventually arrive, after this file was already written from my own read of the docs. It
confirms rather than contradicts the analysis below, and settles one open question: the
confirmed multimodal call shape for every Gemini-based idea here is
`client.interactions.create(model="gemini-3.7-flash", input=[image, prompt], response_format={schema})`,
matching `starter/04_structured_output.py`'s structured-output pattern — no script in the kit
demonstrates the image part specifically, so that plumbing is still the riskiest 20 minutes on
every Gemini-based idea below, exactly as flagged. It also independently confirms the reframe
below was the right call: the only way to make the original live-rerouting version work in 3h
would be hardcoding 2-3 canned board scenarios against a fake schedule file, which fails the
brief's own "judge supplies live input" rule (canned flows read as rehearsed) — so the
zero-external-data reframe stands as originally written, not reverted. One surviving candidate
(Delay-Board Reroute Assistant) needed a hard reframe: as originally scoped it required live
transit/routing data we have no paid API for, so it's replaced below with a same-problem idea
that needs zero external data — everything the answer needs is already in the photo.

Critical grounding fact used throughout: on-device Gemma 4 was **measured on this team's actual
M1 laptop at 4.74 tokens/s** (not the 50-80 tok/s the vendor docs estimate), plus a 65-second cold
load. Every idea below that leans on-device is designed around a **short, structured answer**
(one JSON field, one sentence) for exactly that reason — Gemma is a classifier here, not a writer.

---

```
IDEA 1 — Blind-Spot Wayfinder
Problem in one sentence (a person's words, not a market description):
  "I'm standing at a huge unfamiliar station interchange with zero phone signal and I don't
  know which exit or platform gets me where I'm going."
Who and how often:            Commuters and visitors through big transit interchanges (Bank,
                               King's Cross, Oxford Circus, any large foreign metro), multiple
                               times a week for anyone whose regular commute touches one —
                               platforms and interchange tunnels are exactly where phone signal
                               drops, which is the whole reason this problem exists.
The 90-second wow:            Phone goes into airplane mode on stage. Judge photographs a real
                               posted station map and says a destination out loud ("where's
                               step-free access to the southbound platform?"). Answer appears
                               in under 3 seconds, fully offline.
Google feature named out loud: Gemma 4 E2B/E4B on-device multimodal (image + text) via Ollama —
                               genuinely needs offline, because "you have no signal" is the
                               premise; a cloud call here would contradict the demo's own claim.
Closest existing thing:       Citymapper offline transit maps — https://citymapper.com/news/1196/offline-support
                               — Delta: Citymapper ships pre-digitized data for ~40 major cities;
                               this reads an ad hoc physical map photo from ANY station, never
                               digitized by anyone, and answers from the pixels alone with zero
                               pre-loaded data.
Build in 3h:                  index.html (camera capture, capture="environment"), app.py, 
                               gemma_vision.py (Ollama python client, images=[...] param — NOT
                               demonstrated anywhere in starter/07_local_gemma.py, so this is
                               written from scratch), gemini_fallback.py (quality upgrade path
                               when wifi is up). Riskiest 20 min: getting Ollama's image param
                               working reliably for gemma4:e2b/e4b, and forcing a one-line JSON
                               answer (not prose) to stay inside the measured 4.74 tok/s ceiling
                               — pre-warm the model before the demo, never pay the 65s cold load
                               on stage.
When the API throttles:       Nothing changes — the golden path already runs 100% on-device.
                               Gemini 3.7 Flash is only a silent quality-upgrade fallback when
                               wifi happens to be up; losing it costs nothing visible.
Quotable number:              A wrong-platform detour (avg. ~90 seconds lost) → a 3-second
                               answer, phone in airplane mode.
Which track it fits:          on-device / accessibility
Kill risk:                    Gemma's spatial/OCR reasoning on a real photographed map — angled,
                               glare, crumpled — is untested; a judge-supplied photo that's
                               materially messier than our rehearsed sample is the single
                               likeliest failure, and there's no cloud fallback to catch it
                               because the whole point is offline-only.
```

```
IDEA 2 — Which Row's Mine
Problem in one sentence (a person's words, not a market description):
  "The departure board has 40 rows on it, my train isn't highlighted, and I can't find my
  row before it changes again."
Who and how often:            Commuters at any UK station with a shared multi-row indicator
                               board, multiple times a week — most UK commuter rail runs through
                               interchange or shared-platform stations where scanning a crowded
                               board under time pressure is a daily habit, not an edge case.
The 90-second wow:            Judge says or types one destination ("the next train to Reading")
                               while holding up a real busy departure-board photo. The app
                               isolates just that one row and reads back status + platform in
                               one sentence, in under 2 seconds — judge supplies the input live.
Google feature named out loud: Gemini 3.7 Flash multimodal image input + structured output
                               (response_schema locking the answer to a single row) — needs
                               frontier-tier visual reasoning to reliably parse small, cluttered
                               board text; this is the one idea in the set that leans on Gemini's
                               strength over Gemma's, and says so honestly rather than forcing an
                               on-device story that wouldn't hold up.
Closest existing thing:       Citymapper / National Rail Live Departure Boards — Delta: those
                               apps show their OWN live data feed; this reads a photo of a
                               physical board — any board, any country, none of it pre-integrated
                               into any transit app's data pipe — and answers purely from the
                               pixels in front of you, no live transit API, no data feed needed.
                               (Reframed from an earlier "reroute" version of this idea that
                               needed live transit data we have no paid API for — this version
                               needs zero external data, since the answer is already in the photo.)
Build in 3h:                  index.html (camera + voice/text destination field), app.py,
                               board_reader.py (Gemini Interactions API: image + destination →
                               {row, platform, status} via response_schema), gemma_fallback.py
                               (same schema, on-device, degraded accuracy). Riskiest 20 min:
                               reliably isolating one row out of many via prompt + schema — test
                               against 3-4 real board photos ahead of time, small/blurry text at
                               the frame edges is the likely failure mode.
When the API throttles:       Falls back to on-device Gemma4 E2B with the identical JSON schema
                               (worse accuracy, still functional); demo pre-caches 2-3 known
                               board photos so a mid-demo throttle can replay a cached response
                               instantly rather than visibly stall.
Quotable number:              Scanning 40 rows under pressure → reading one sentence.
Which track it fits:          agents / productivity
Kill risk:                    A judge's own live phone photo (glare, angle, small font) may not
                               parse as cleanly as rehearsed sample images — the gap between
                               rehearsal and a genuinely judge-supplied input is the real risk.
```

```
IDEA 3 — Cycling Rule Decoder
Problem in one sentence (a person's words, not a market description):
  "I'm on my bike looking at a sign with three stacked symbols on one pole and I don't know
  if I'm allowed to ride through here right now."
Who and how often:            UK cyclists commuting through mixed-use paths, shared spaces, and
                               contraflow junctions — multiple times a week for the regular bike
                               commuter population (hundreds of thousands of daily London cycle
                               journeys alone); narrower audience than the transit ideas, flagged
                               honestly rather than inflated to "every adult."
The 90-second wow:            Judge is handed a photo of a real confusing UK cycling sign
                               (shared path / "cyclists dismount" / contraflow arrow / no-entry-
                               except-cycles) and asks "can I ride through here right now?" —
                               one plain sentence back, quoting the specific rule, under 2 seconds.
Google feature named out loud: Gemini 3.7 Flash multimodal image input, reasoning over a short
                               pre-loaded Highway Code cycling-signs reference passed in context
                               (not live search) — needs frontier-tier disambiguation between
                               near-identical sign symbols (shared path vs. segregated path vs.
                               dismount) that a small on-device model would likely confuse.
Closest existing thing:       DfT "Know Your Traffic Signs" app —
                               https://apps.apple.com/gb/app/dft-know-your-traffic-signs/id6466648716
                               — Delta: that's a manual browse-by-1000-signs reference (you must
                               already know which sign to look up); this is photo-in/verdict-out,
                               zero searching, and combines multiple stacked signs into one
                               situational answer instead of one sign's dictionary definition.
Build in 3h:                  index.html (camera capture), app.py, sign_reader.py (Gemini call
                               with a short hand-curated Highway Code cycling-rules cheat sheet
                               as context + response_schema for {allowed: bool, rule_cited}),
                               gemma_fallback.py. Riskiest 20 min: writing an accurate, honest
                               cheat sheet of the real Highway Code cycling rules to ground the
                               model on — get this wrong and the app gives a confidently wrong
                               answer; this is the real risk, not the API call itself.
When the API throttles:       On-device Gemma4 E2B with the same cheat sheet in its short
                               context window — degraded confidence, same golden path.
Quotable number:              A 30-second squint at a confusing sign → a 2-second verdict.
Which track it fits:          on-device / safety
Kill risk:                    This edges into "rules of the road" territory — a wrong verdict on
                               stage (or a judge's own known-tricky sign) reads as safety-relevant
                               misinformation, exactly where the brief warns judges poke. Needs a
                               hard, visible "informational, not a legal ruling" disclaimer to
                               survive that question.
```

```
IDEA 4 — Missed-Parcel Slip Decoder
Problem in one sentence (a person's words, not a market description):
  "I got home to a card through the door with a cryptic code on it and no idea which courier
  left it or what I'm supposed to do next."
Who and how often:            Anyone who shops online, multiple times a week in busy or
                               multi-occupancy UK households — missed-delivery cards are a
                               near-weekly occurrence wherever online shopping volume is high
                               and someone isn't always home.
The 90-second wow:            Judge is handed a real UK missed-delivery card (Royal Mail, Evri,
                               DPD, Yodel all differ) and the app instantly explains in plain
                               language what happened, which courier it is, and the concrete
                               next step — reading the card only, never clicking any link on it.
Google feature named out loud: Gemini 3.7 Flash multimodal image input + structured output —
                               needs strong OCR-plus-reasoning to identify which of several
                               near-identical UK courier card formats it's looking at and map
                               that format's own codes correctly.
Closest existing thing:       Parcel Tracker (700+ carrier barcode scanner) —
                               https://www.parceltracker.com/ — Delta: Parcel Tracker needs you
                               to already know/select the courier and scan a barcode for a live
                               tracking feed; this reads an unfamiliar card cold, identifies the
                               courier itself from visual formatting, and explains the card's own
                               printed instructions rather than pulling a live tracking feed.
Build in 3h:                  index.html (camera capture), app.py, slip_reader.py (Gemini call +
                               response_schema for {courier, code_meaning, next_step, deadline}),
                               gemma_fallback.py. Riskiest 20 min: sourcing 3-4 real sample card
                               images across different UK couriers to test against ahead of time
                               — one tested format looks like a demo, not a product.
When the API throttles:       On-device Gemma4 E2B, same schema; dense small print is the main
                               accuracy hit, not availability.
Quotable number:               A confusing card and a maybe-scam-looking QR code → one trustworthy
                               sentence, no link clicked.
Which track it fits:          productivity / accessibility
Kill risk:                    The problem shape — photo of a delivery card → instructions — is
                               visually identical to the exact phishing pattern NCSC actively
                               warns UK consumers about (ncsc.gov.uk/guidance/scam-missed-parcel-sms-messages).
                               A judge who's seen that warning may instinctively distrust the
                               pitch unless "we never open a link, we only read the card already
                               in your hand" is stated explicitly and first.
```

```
IDEA 5 — Carry-On Security Checker
Problem in one sentence (a person's words, not a market description):
  "I've laid everything out on the bed for my carry-on and I won't find out what security
  is going to confiscate until I'm already through the scanner."
Who and how often:            Weakest frequency claim of the five, flagged deliberately rather
                               than oversold: most adults fly a handful of times a year, not
                               weekly. The honest argument is per-trip stakes (confiscation, a
                               missed flight) rather than a weekly habit — this is the one idea
                               here most exposed to the brief's own "frequency" filter.
The 90-second wow:            Judge lays out a phone, a toothpaste tube, a multitool, and a
                               power bank and photographs the pile in one shot — app flags
                               exactly which items get pulled at UK security and why, one
                               sentence per item, under 3 seconds.
Google feature named out loud: Gemini 3.7 Flash multimodal image input + structured output —
                               needs to detect and classify multiple distinct physical objects
                               in one cluttered photo simultaneously, not OCR a single label.
Closest existing thing:       MyTSA "Can I Bring?" — https://www.tsa.gov/travel/security-screening/whatcanibring/all
                               — Delta: MyTSA is a manual one-item-at-a-time text search (type
                               "toothpaste," get an answer); this is one photo of an entire
                               packed bag, multi-item detection in a single pass, zero typing.
Build in 3h:                  index.html (camera capture), app.py, bag_scanner.py (Gemini call +
                               response_schema returning a list of {item, verdict, rule}),
                               gemma_fallback.py. Riskiest 20 min: multi-object detection
                               reliability in one cluttered photo — small/overlapping items (a
                               power bank half-hidden under a jumper) are the likely miss case;
                               test with a deliberately messy sample bag ahead of time.
When the API throttles:       On-device Gemma4 E2B, same schema, but multi-object recall in a
                               single small model is materially worse — the honestly weakest
                               fallback of the five ideas here.
Quotable number:              One glance at a packed bag → no confiscated power bank at the gate.
Which track it fits:          on-device / productivity
Kill risk:                    The frequency argument is this idea's real weak point against the
                               brief's own filter #2 — "multiple times a week" doesn't hold for
                               ordinary flying habits. Cut this one first if the announced track
                               rewards daily-habit framing over per-trip-stakes framing.
```

---

## Ranking, best first

1. **Blind-Spot Wayfinder** — the only idea where "offline" is structurally necessary, not
   bolted on: the premise (no signal) is the reason to demo it live in airplane mode, which is
   the single cleanest way to make a judge feel the on-device story. Cleanest prior-art delta
   found, no paid API anywhere in the build, and its short-answer shape is a natural fit for
   Gemma's measured 4.74 tok/s ceiling rather than fighting it.
2. **Which Row's Mine** — best frequency claim of the five (commuting is genuinely a
   multiple-times-a-week habit), zero external data dependency after an honest reframe away
   from live rerouting, and a crisp single golden path. Ranked second only because it leans on
   Gemini cloud rather than on-device, which is slightly less on-brand for a room built around
   both keynotes.
3. **Cycling Rule Decoder** — genuine, well-evidenced prior-art delta and cleanly offline-
   capable, but the audience is narrower (regular cyclists, not every adult) and it carries a
   real legal-adjacent kill risk that needs a disclaimer built in from the start, not bolted on
   after a bad question.
4. **Missed-Parcel Slip Decoder** — solid frequency and a real, if narrow, delta, but the
   phishing-card resemblance is a genuine first-impression risk with this specific judging
   panel; salvageable only if the "we never click a link" framing lands in the first ten
   seconds of the pitch.
5. **Carry-On Security Checker** — the strongest prior-art delta of all five (no shipped
   whole-bag-photo scanner found anywhere), but the weakest frequency argument against the
   brief's own filter. Ranked last specifically because of that gap, not because the build or
   the wow moment are weak.
