# Home, Food & Chores — candidate ideas

Domain scout brief: notes/plans/2026-08-22-cross-model-prompt.md. Ground truth: docs/00-ground-truth.md.
Camera-as-input is the deliberate thread through all 5 — a judge can point a phone at any real
object in the room, which is exactly the judge-supplied-input the brief rewards.

**Process note (honesty, not filler):** 7 draft candidates were sent to two parallel subagents —
a prior-art hunter (researcher, web search) and a feasibility prover (engineer, read the starter
kit + docs/03 + docs/05 + docs/07). Of the original 7, the prior-art hunter hard-**KILLED 3**
(food-freshness scanners, care-label decoders, and receipt-to-expiry trackers are all already
shipped multiple times over — see kill log at the bottom) and I dropped 2 more myself on the
**frequency** hard filter (flat-pack furniture assembly and utility-meter reading are not
multiple-times-a-week problems for an ordinary adult, even though both cleared prior art and
feasibility). That left only 1 clean survivor. I generated 3 replacement ideas using the pattern
that actually survived scrutiny — multi-object cross-referencing or personalized/inventory-
constrained reasoning, not a single photo against a static lookup table, which is the saturated
shape. **Those 3 replacements were not independently web-verified by the prior-art subagent**
(time-boxed at 12 minutes) — I've flagged confidence honestly in each "Closest existing thing"
field rather than overclaiming novelty.

All 5 share the same build-risk finding from the feasibility subagent: the starter kit
(`starter/*.py`) has **zero multimodal image-input examples** — every script is text/audio only.
`docs/03-gemini-3.7-flash.md` confirms `gemini-3.7-flash` accepts image input, but the exact
`interactions.create(...)` call shape for an image (or two images) is unverified in this repo.
**Whichever idea is picked, spend the first 15-20 minutes proving one working image call before
building anything on top of it** — that spike is the real go/no-go gate, not any single idea's
specific risk.

---

```
IDEA 1 — Cleaning Product Matcher
Problem in one sentence: I don't know which of these three sprays under my sink is actually safe
  to use on this stain, or whether mixing two of them is dangerous.
Who and how often:            Every UK household wipes kitchen/bathroom surfaces daily and does a
  fuller clean 2-3x/week; the "which product, and is it safe to combine" hesitation happens on
  most of those passes. Accidental bleach+ammonia/bleach+acid mixing is a real, recurring
  household hazard, not a hypothetical.
The 90-second wow:            Judge hands over two real products from under a sink (or a staged
  pair) plus points the camera at a stained surface. App photographs both in one shot and says,
  live: "Don't use Product A on Product B's residue — bleach + ammonia — ventilate and use Product
  C on this surface for 2 minutes instead."
Google feature named out loud: Gemini 3.7 Flash multimodal — two images in one call, structured
  output identifying products/materials, then agentic reasoning that cross-references a small
  internal hazard-pairs table via function calling. A single-image classifier couldn't catch a
  cross-product interaction; this needs the multi-image + tool-calling combination.
Closest existing thing:       CleanBot AI (apps.apple.com/us/app/cleanbot-ai-stain-solution/id6758080832)
  — photographs a stain, recommends an abstract cleaning solution. Delta: this photographs the
  user's ACTUAL under-sink products (inventory-constrained, not generic advice) and explicitly
  flags dangerous chemical interactions between them — CleanBot's listing does neither.
Build in 3h:                  app.py (Flask), templates/index.html (2-photo upload UI),
  static/app.js, gemini_client.py (wraps starter's get_client/DEFAULT_MODEL/with_retry),
  hazard_pairs.json (small hand-curated list: bleach+ammonia, bleach+vinegar, bleach+stone, etc.),
  requirements.txt. Deploy via Render/Fly free tier. Riskiest 20 min: the untested 2-image-in-one-
  call multimodal shape — spike this first, everything else is routine Flask.
When the API throttles:       Stage one guaranteed-good demo pair (bleach spray + ammonia-based
  glass cleaner) tested and cached in advance; serve the cached response on 429/timeout so the
  danger-flag moment never stalls. Gemma 4 on-device as an offline fallback for basic material ID
  if wifi dies entirely.
Quotable number:              Turns a guess that risks a real household chemical accident into a
  3-second, confidently-sourced answer.
Which track it fits:          safety / accessibility
Kill risk:                    A hallucinated or missed hazard warning live on stage undermines
  trust instantly. Never let a judge supply fully random products for the safety-flag part of the
  demo — rehearse with a guaranteed-good pair and keep judge-supplied input to the surface/stain
  half of the shot.
```

```
IDEA 2 — Appliance Control Panel Decoder
Problem in one sentence: This washing machine/oven has ten unlabeled icons and I have no idea
  which one means what I actually need right now.
Who and how often:            Everyone operates a washing machine, oven, dishwasher, or microwave
  multiple times a week; unlabeled, foreign-language, or inherited/rental appliances are common in
  UK shared housing, so the "what does this icon mean" moment recurs constantly.
The 90-second wow:            Judge points a phone at any appliance control panel (a real one, or
  a photo on a laptop screen) and says out loud "I want to wash a wool jumper" or "I want to
  defrost chicken." App reads the icons and states exactly which dial position or button sequence
  to use, and why.
Google feature named out loud: Gemini 3.7 Flash multimodal image understanding chained to agentic
  reasoning that connects a stated goal to icon interpretation it has never seen laid out exactly
  this way before — not a fixed lookup table, a genuine reasoning step.
Closest existing thing:       Manual-finder tools (ManualsLib, Klippa's document-scanning SDK)
  retrieve a PDF manual once they've identified the exact model. Delta: no model identification
  needed at all — reasons directly from the visible icons to a goal-directed answer, so it works
  on unbranded, foreign, or manual-less appliances too. Not independently web-verified by the
  prior-art subagent (generated after its run) — flagged as medium confidence, not certain.
Build in 3h:                  app.py, templates/index.html (photo + free-text goal field),
  static/app.js, gemini_client.py, requirements.txt — no curated dataset needed, this is pure
  visual-plus-reasoning. Deploy via Render/Fly free tier. Riskiest 20 min: same multimodal
  call-shape spike as Idea 1, plus prompting carefully enough that icon interpretation doesn't
  hallucinate a confidently-wrong setting.
When the API throttles:       3-4 pre-shot real appliance photos (washing machine, oven,
  dishwasher) with cached goal-to-answer pairs as instant fallback. Gemma 4 on-device for a basic
  offline icon-description pass if wifi dies completely.
Quotable number:              Turns 10 minutes of guessing (and the odd ruined load of laundry)
  into a 5-second answer.
Which track it fits:          accessibility / productivity
Kill risk:                    Confidently wrong icon interpretation on a panel layout the model
  hasn't effectively seen before. Rehearse against 3-4 genuinely varied real panels beforehand so
  the live demo lands near a rehearsed layout, don't accept a judge's totally novel obscure panel
  cold.
```

```
IDEA 3 — Laundry Pile Sorter
Problem in one sentence: I've got a pile of clean-but-mixed laundry and no idea which of these can
  actually go in the same wash without ruining something.
Who and how often:            Most households do laundry 2-4 times a week, and the "can this go in
  with that" moment happens every single load, not occasionally.
The 90-second wow:            Judge lays out a small mixed pile of garments (a dark top, a white
  shirt, one delicate item) in front of the camera in one shot. App groups them into wash-load
  buckets — whites/40C, darks/30C, hand-wash-only — and explains out loud why the delicate item
  was pulled out.
Google feature named out loud: Gemini 3.7 Flash multimodal doing genuine multi-object reasoning in
  a single image (color, fabric texture, and visible label symbols across several garments at
  once) — not a single-item classification call.
Closest existing thing:       Care-label scanner apps like Laundry Master
  (apps.apple.com/us/app/laundry-master-care-label/id6756978100) decode one garment's label per
  scan. Delta: this reasons across a whole pile at once to solve the actual weekly decision —
  which combination is safe to wash together — a batch/combinatorial judgment none of the
  single-label scanners attempt. Not independently web-verified by the prior-art subagent
  (generated after its run) — medium confidence.
Build in 3h:                  app.py, templates/index.html (single pile-photo upload),
  static/app.js, gemini_client.py, requirements.txt — no curated dataset, fabric/wash-symbol
  knowledge is broad training knowledge. Deploy via Render/Fly free tier. Riskiest 20 min: the
  multimodal call spike, plus getting reliable multi-object reasoning from one photo instead of
  the model latching onto only the most prominent garment.
When the API throttles:       Pre-shot pile photo with a cached sorted result as instant fallback.
  Gemma 4 on-device for basic color-only sorting offline (a simpler task, more robust locally).
Quotable number:              Cuts the "wait, can this go in with that?" guess to under 5 seconds
  — no more faded whites or shrunk wool.
Which track it fits:          productivity / accessibility
Kill risk:                    Pile photos are visually messy; overlapping garments could produce a
  shaky read. Keep the rehearsed pile to 4-5 clearly separated items, not a crumpled heap, and
  steer a judge's live pile the same way.
```

```
IDEA 4 — Bin Whisperer (reframed)
Problem in one sentence: I'm holding this weird bit of packaging and I genuinely don't know which
  bin it goes in, or whether I'm about to contaminate the whole recycling load.
Who and how often:            Every UK household sorts rubbish/recycling daily — arguably the
  single highest-frequency problem in this domain.
The 90-second wow:            Judge hands over a real piece of rubbish (a greasy pizza box, a
  crisp packet, a coffee cup) live. App names the bin AND narrates the contamination reasoning
  ("there's grease in this corner — that contaminates a whole batch of recycling, so general
  waste"), then instantly re-answers for a second London borough to show the rules genuinely
  differ by postcode.
Google feature named out loud: Gemini 3.7 Flash multimodal image classification, agentic
  tool-calling into a small borough-rules lookup, chained into a second reasoning step that
  explains WHY, not just WHAT.
Closest existing thing:       West Northamptonshire Council's own in-app AI recycling scanner
  (westnorthants.gov.uk/news/enhanced-app-launched-make-everyday-services-easier) already does
  photo -> council-tailored disposal guidance, shipped, live. This is a real, close prior-art hit
  — the honest delta is narrower than the other four ideas here: showing the live contamination-
  reasoning chain and a cross-borough comparison in one demo, not the flat photo-to-bin lookup a
  council app already provides. Weakest novelty claim of the five.
Build in 3h:                  app.py, templates/index.html, static/app.js, gemini_client.py,
  council_rules.json (hand-curated, 3-4 London boroughs x ~20 materials). Deploy via Render/Fly
  free tier. Riskiest 20 min: the multimodal call spike, plus sourcing accurate real council rules
  fast without hallucinating them.
When the API throttles:       Preset gallery of 5-6 real rubbish photos with cached results;
  borough lookup is pure Python so it works instantly once material is identified.
Quotable number:              Turns "I have no idea which bin this goes in" into a confident,
  reasoned answer in under 3 seconds — and catches a contamination mistake before it happens.
Which track it fits:          safety / accessibility
Kill risk:                    The prior art is real and close — a UK council already ships almost
  this exact feature. A judge or a fellow participant who's seen it could call this out directly
  on stage; this is the single highest prior-art risk of the five. Include only if the team can
  sell the reasoning-chain framing hard, or swap it out first if a stronger idea surfaces.
```

```
IDEA 5 — Grocery Shelf Duplicate-Buy Preventer
Problem in one sentence: I'm not sure if I already have three tins of chopped tomatoes at home, so
  I either double-buy or come home empty-handed.
Who and how often:            Most UK households do a big shop plus a top-up shop, roughly 2x/week;
  the "do I already have this" hesitation happens on nearly every aisle of every trip.
The 90-second wow:            Judge photographs a "pantry shelf" prop (a few labeled tins/boxes)
  with their phone, then says an item out loud ("chopped tomatoes"). App instantly answers "you've
  got 3, skip it" or "you're out, add it," reasoning purely from what's visible in the shelf photo
  — no account, no persistent database.
Google feature named out loud: Gemini 3.7 Flash multimodal — single-shot visual inventory
  reasoning against a spoken/typed query, agentic enough to count and identify specific items
  rather than a fixed barcode lookup.
Closest existing thing:       NoWaste (nowasteapp.com) and Fridgely (fridgelyapp.com) build a
  persistent inventory from receipt scans over time and track expiry — this is a genuinely
  crowded, prior-KILLED category for the receipt-scan variant (see kill log). Delta here: no
  account or receipt history at all — a single disposable shelf-photo snap-decision used in the
  moment before/during a shop, answering "do I already have this" rather than "when does this
  expire," sidestepping their entire onboarding/inventory-building workflow. Not independently
  web-verified — medium-low confidence given how crowded this category is.
Build in 3h:                  app.py, templates/index.html (photo + spoken/typed item query),
  static/app.js, gemini_client.py, requirements.txt — stateless, no curated data. Deploy via
  Render/Fly free tier. Riskiest 20 min: the multimodal call spike, plus reliable counting of
  small/similar-looking tins in one photo.
When the API throttles:       Pre-shot shelf photo with a small cached set of query-to-answer
  pairs as fallback.
Quotable number:              Turns a "maybe I already have this" guess into a 3-second yes/no,
  right there in the aisle.
Which track it fits:          productivity
Kill risk:                    Weakest frequency claim of the five (2x/week shopping trips, not
  daily) and sits closest in spirit to the crowded pantry-inventory app category even though the
  mechanism differs. Likely the first idea to cut if the team needs to trim to a stronger four.
```

---

## Ranking (best first)

1. **Cleaning Product Matcher** — only idea that cleared prior art AND feasibility cleanly on the
   first pass; genuine safety-flagging delta a judge can feel in one demo.
2. **Appliance Control Panel Decoder** — strongest frequency + wow of the replacements, clean
   differentiation from the already-considered "point-and-diagnose broken appliance" idea (this
   decodes a *working* appliance's UI, not a fault).
3. **Laundry Pile Sorter** — solid frequency, plausible novelty via multi-object reasoning, but
   unverified against prior art under time pressure.
4. **Bin Whisperer (reframed)** — the best 90-second wow of the five (a judge hands you literal
   rubbish live) but carries real, named prior art from a UK council; keep only if the team commits
   to selling the reasoning-chain angle hard.
5. **Grocery Shelf Duplicate-Buy Preventer** — weakest frequency claim and sits nearest a
   saturated category; first to cut under pressure.

## Kill log (dropped, do not resurrect without a new angle)

- **Is This Still Good?** (fridge/pantry item freshness scanner) — prior-art hard KILL: Fresh
  Checker, SPOIL, Moldy, Fruit Scanner already ship exactly this, including cue-level reasoning.
  Also brushes the medical/safety-advice hard filter.
- **Laundry Rescue** (care-label decoder + fabric-specific stain removal) — prior-art hard KILL:
  Laundry Master already ships this exact two-part combo.
- **Receipt Countdown** (grocery receipt -> use-by countdown) — prior-art hard KILL: NoWaste and
  Fridgely already ship receipt-to-waste-triage, framed the same way ("not a recipe app" doesn't
  create distance from either).
- **Flat-pack Rescue** (photo of a confusing IKEA-style step + loose parts) — cleared both prior
  art and feasibility, dropped by me on the frequency hard filter: furniture assembly is not a
  multiple-times-a-week problem for an ordinary adult.
- **Home Admin Snap** (utility meter photo -> reading + anomaly log) — cleared both prior art and
  feasibility, dropped by me on the frequency hard filter: meter reading is a monthly event at
  best.
