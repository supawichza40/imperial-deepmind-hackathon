# Cross-model idea run — Fable 5 (independent, no coordination)

## Where I looked that the brief did not suggest

I went at the physical, offline layer of adult life — the doormat pile, the appliance control panel, the laundry basket, the car-boot sale, the back seat of the car — on the theory that app stores have strip-mined single-shot "point camera, get answer" apps (I killed four of my first candidates that way: AI listing generators, home-inventory AI, paper-form voice fillers, and unit-price camera scanners are all shipped), so the surviving white space is not a new *object* to point at but a new *side of the transaction*: the buyer not the seller in secondhand, the helper not the learner in family tech support, the person sharing the photo not the platform receiving it. That helper-side/adversarial-side framing is also what makes each idea genuinely need agentic multi-step tool use or on-device privacy — the two keynotes — rather than wearing them as stickers.

---

```
IDEA 1 — Second Look
Problem in one sentence (a person's words, not a market description): "This sofa/bike/PS5 on Marketplace looks like a bargain but I don't know what it's actually worth or what's wrong with this model, and the seller knows more than me."
Who and how often:            Anyone buying secondhand — Vinted, eBay, FB Marketplace, car-boot sales. UK secondhand buying is habitual: active users browse listings several times a week and weigh up a purchase 2-3x/week (JUDGEMENT from platform usage patterns; Vinted alone claims ~16M UK users). Every purchase decision is this problem.
The 90-second wow:            Judge opens any live listing on their own phone and screenshots it into the app (or points our camera at a real object we brought). On screen, the agent's steps run visibly one by one: "identifying: Ercol dining chair, ~1970s" → "searching sold comps" → "searching known faults" → verdict card: "Asking £140, recent sold range £70–95. Check the seat joints — this model's glue fails. Ask the seller these 3 questions." Judge supplied the input; nothing was canned.
Google feature named out loud: Gemini 3.7 Flash agentic tool calling with Google Search grounding — the idea IS a visible multi-step research agent (identify → comps → faults → verdict); a single prompt cannot do it because the value is in live sold-price data.
Closest existing thing:       Spottable (Chrome extension, FB Marketplace deal scorer) https://chromewebstore.google.com/detail/spottable-facebook-market/dbgjphnanjmmfjacahfhliahblokmpgh ; Meta is also testing buyer "suggested questions" https://techcrunch.com/2026/03/12/facebook-marketplace-now-lets-meta-ai-respond-to-buyers-messages/ — Delta: platform-agnostic (screenshot from ANY marketplace, or camera at a physical object at a car-boot sale — no extension, no FB account), plus model-specific known-fault research, not just price scoring. The in-person camera mode has no shipped equivalent.
Build in 3h:                  main.py (FastAPI: one /analyze endpoint driving a Gemini function-calling loop with tools identify_item / search_comps / search_faults via Search grounding), index.html (image paste + camera + live agent-step timeline UI), deploy `gcloud run deploy --source .` to Cloud Run. Riskiest 20 minutes: chaining 3-4 grounded calls per query under free-tier latency — pre-cache fault-sheets for 5 common demo categories so the chain never exceeds 2 live calls.
When the API throttles:       Queue with visible "researching…" states (the agent timeline makes waiting look like work); if fully throttled, Gemma 4 local fallback runs a category-level checklist ("used bike: check these 6 things") from a cached corpus — degraded but never blank.
Quotable number:              "15 minutes of nervous googling → 30 seconds, and it caught a £45 overpricing live on stage."
Which track it fits:          agents / productivity
Kill risk:                    Venue wifi dies mid-chain — the one idea here that needs live search to deliver its wow. Mitigation is the cached-category fallback, but the sold-comps moment is the wow, and it is network-dependent.
```

```
IDEA 2 — Doormat
Problem in one sentence (a person's words, not a market description): "There's a pile of post on the side and I genuinely don't know if something in it has a deadline that's going to bite me."
Who and how often:            Every UK household gets letters most days — council, HMRC, NHS appointments, parking, insurance renewals. The pile builds daily; the guilt-triage happens 2-4x/week (JUDGEMENT: Royal Mail still delivers ~6B addressed letters/year; life-admin letters cluster on ordinary adults, especially renters and parents).
The 90-second wow:            We turn wifi OFF. Judge pulls any letter from their own bag (or takes one from our stack of 8 real ones), holds it to the camera: Gemma reads it on-device and the letter lands on a triage board — ACT BY 5 SEP / FILE / BIN / SCAM?. Then wifi back ON: Gemini's verification agent enriches the extracted deadline against the real gov.uk page and a one-tap .ics file adds it to any calendar with no login. The pile of 8 letters becomes a triage board in 90 seconds.
Google feature named out loud: Both keynotes in one split: Gemma 4 on-device (LiteRT) reads the private letter — your post never leaves the room — and Gemini 3.7 Flash with Search grounding verifies deadlines/reference context on the redacted extract only. The privacy split is the architecture, not a slide.
Closest existing thing:       LetterMagic https://play.google.com/store/apps/details?id=com.builtbyboard.Lettermagicfrontend and Papeer https://papeer.ai/ (scan letters, extract deadlines — both cloud) — Delta: on-device read of the sensitive full text (cloud apps upload your NHS letter; we provably don't — wifi-off demo), whole-pile sweep rather than letter-at-a-time, and no-login .ics export instead of an in-app todo silo.
Build in 3h:                  index.html (camera capture, board UI, client-side ICS generation, MediaPipe LLM Inference running Gemma 4 E2B in-browser via WebGPU), main.py (FastAPI proxy for the Gemini enrich path), Cloud Run. Riskiest 20 minutes: in-browser Gemma multimodal load on an unknown judge laptop — fallback path is server-side Gemma/Gemini with the on-device demo done on our laptop.
When the API throttles:       The core read is local, so throttling only delays the enrichment column; board still fills offline. This idea is built to survive dead wifi — that IS the pitch.
Quotable number:              "A week of doormat pile → 90 seconds, and the NHS letter never left the kitchen."
Which track it fits:          on-device / productivity / safety
Kill risk:                    Judges pattern-match it to "document summarizer" (anti-template filter) before the wifi-off moment lands. The demo must open with the router being unplugged, not with the upload button.
```

```
IDEA 3 — Overshare Check
Problem in one sentence (a person's words, not a market description): "I'm about to post this photo and I have no idea what's in the background that I'd regret."
Who and how often:            Anyone who shares photos — which is most adults, daily (school WhatsApp groups, socials, selling photos, holiday posts). The regret-scan is implicit in every share; nobody actually does it.
The 90-second wow:            Airplane mode on. Judge takes a photo right there in the venue. Eight seconds later, on-device: "This photo tells a stranger: your full name (badge, bottom left), your employer, the wifi password on the whiteboard, an email inbox on the laptop behind you." Each leak is narrated as an inference chain ("badge + lanyard colour → attendee list → LinkedIn"), then one tap blurs them all. The venue is FULL of badges and screens — the room is the demo.
Google feature named out loud: Gemma 4 multimodal on-device via LiteRT — non-negotiable for this idea: a privacy scanner that uploads your photos to a cloud is a contradiction, and we say that sentence to the judges.
Closest existing thing:       Lookr: AI Photo Privacy https://apps.apple.com/in/app/lookr-ai-photo-privacy/id6761846110 (AI scan for faces/plates/signs, blur) — Delta: Lookr detects object classes and blurs; we narrate the inference chain (what a stranger could DO with each element), which is what changes behaviour, and we run fully offline in the browser rather than as an iOS app.
Build in 3h:                  index.html only, fully client-side: MediaPipe LLM Inference (Gemma 4 E4B multimodal) + canvas blur regions from model-returned boxes; static deploy on Cloud Run or Firebase Hosting. Riskiest 20 minutes: box coordinates from the VLM being sloppy — fallback is region-free mode: numbered callout list + tap-to-blur-quadrant, which still demos.
When the API throttles:       No API in the golden path. Cloud Gemini exists only as an optional "deep scan" toggle clearly labelled as leaving the device.
Quotable number:              "4 leaks found in the judge's own photo, in 8 seconds, in airplane mode."
Which track it fits:          safety / on-device
Kill risk:                    A false negative on stage — it misses an obvious leak and the room laughs. Mitigation: never claim exhaustive ("what I can see so far…"), and the badge/screen-dense venue makes hits near-certain.
```

```
IDEA 4 — Which Button
Problem in one sentence (a person's words, not a market description): "I'm standing in front of this machine — coffee machine, hotel thermostat, launderette dryer, office dishwasher — and I don't know which button does the thing I want."
Who and how often:            Everyone meets unfamiliar control panels a few times a week — the office coffee machine, someone else's washing machine, hotel AC, car dashboards, AV panels (JUDGEMENT: this is the 'stand there jabbing buttons' moment everyone recognizes; manuals are long gone).
The 90-second wow:            We walk the judge to the venue's own coffee machine. They point the phone at it and say "make it stronger." The panel comes back annotated — each button labelled — with three spoken steps for the goal. Offline. The judge picks the machine and the goal; nothing can be rehearsed because we don't choose the panel.
Google feature named out loud: Gemma 4 multimodal on-device (LiteRT) — panels live in basements, launderettes and kitchens where wifi doesn't, and the response must be instant to beat just jabbing buttons.
Closest existing thing:       Google Lens (identifies objects, doesn't do goal-directed control-panel guidance) https://lens.google/ ; Manualslib (manual database, needs the model number and reading 40 pages) https://www.manualslib.com/ — Delta: goal-in, steps-out on a live camera view of an arbitrary panel, no model number, no manual, no network.
Build in 3h:                  index.html client-side (camera frame → Gemma 4 E4B multimodal → JSON of button labels + step list → SVG overlay + Web Speech TTS), static deploy. Riskiest 20 minutes: overlay alignment on reflective panels — fallback is a captured still with numbered circles instead of live AR, which loses nothing in the pitch.
When the API throttles:       Fully local golden path; no API involved.
Quotable number:              "Manual hunting: 10 minutes if you're lucky. This: 10 seconds, on the venue's own coffee machine."
Which track it fits:          on-device / accessibility / productivity
Kill risk:                    Hallucinated button functions on an obscure panel in front of the one judge who owns that machine. Mitigation: confidence phrasing ("likely the eco toggle — test with a short press") and steering the live demo to common machine types.
```

```
IDEA 5 — Big Font
Problem in one sentence (a person's words, not a market description): "Mum's sent me a photo of her phone screen again and I'm about to spend 40 minutes on the phone saying 'no, the OTHER settings icon'."
Who and how often:            The sandwich generation — adults fielding tech-support pings from parents 1-3x/week (JUDGEMENT: remote family tech support is a near-universal recurring chore for adults with parents over 65; every carer forum jokes about it).
The 90-second wow:            Judge screenshots anything on their own phone, uploads it as "what my mum sent me," and types her question ("how do I make the writing bigger?"). Out comes two artifacts: a printable A4 with 4 numbered steps in 20pt type, each with a cropped, arrowed piece of HER actual screenshot — and a 30-second phone script ("tell her: tap the gear that looks like a cog, bottom right"). Print it, hand it to the judge.
Google feature named out loud: Gemini 3.7 Flash multimodal + structured output: it must read an arbitrary phone screenshot, ground each step in a crop of that exact screenshot, and emit a print-ready artifact — image-grounded structured generation, not chat.
Closest existing thing:       Duca (step-by-step tech help aimed at the older adult themselves) https://apps.apple.com/us/app/duca-step-by-step-tech-help/id6737066104 ; Apo by Carevocacy https://thegerontechnologist.com/the-first-ai-tech-support-for-older-adults-apo-by-carevocacy/ — Delta: we serve the HELPER, not the learner: input is the relative's actual screenshot, output is a physical artifact (big-font printable + say-aloud script) tuned for someone who will never install an app.
Build in 3h:                  main.py (FastAPI, Gemini multimodal → JSON steps + crop boxes), index.html + print.css (A4 layout, browser print), Cloud Run. Riskiest 20 minutes: reliable crop-box coordinates from the screenshot — fallback: full screenshot per step with a drawn arrow, still entirely usable.
When the API throttles:       Requests are single-shot (one screenshot, one call) so 15 RPM is ample; on hard throttle, Gemma local produces text-only steps and the crops are skipped.
Quotable number:              "The 45-minute Sunday phone call → a 2-minute printable."
Which track it fits:          accessibility / productivity
Kill risk:                    Reads as "wrapper that explains a screenshot" if the printable isn't visibly beautiful — the artifact IS the product, so the print.css polish cannot slip.
```

```
IDEA 6 — Backseat Games
Problem in one sentence (a person's words, not a market description): "We're stuck in the car / GP waiting room, the kids are melting down, and the only tool I have is handing over my phone."
Who and how often:            Parents of under-10s hit the entertain-them-NOW moment daily; car journeys and waiting rooms specifically several times a week. The current solution (screen time) is the thing parents feel worst about.
The 90-second wow:            Judge empties their pockets onto the table — keys, receipt, mints, a lanyard. Photo. Airplane mode is already on. Twenty seconds later Gemma invents a playable game from exactly those objects ("Border Control: the mints are contraband, the lanyard is the scanner…"), with rules for two players, and then referees it by voice, keeping score. A different pocketful yields a different game — provably not canned.
Google feature named out loud: Gemma 4 E4B on-device: multimodal (sees the objects) + native on-device function calling (the referee calls local score/timer functions) + offline (cars and waiting rooms have no signal). This is the Gemma keynote demo'd as family life.
Closest existing thing:       AI Toys action-figure generators (photo → toy RENDER, not play) https://play.google.com/store/apps/details?id=com.garage.labs.ai.banana.toys.action.figures.generator ; FoloToy conversational toys (hardware, cloud) https://folotoy.com/ ; non-AI activity-list apps — Delta: nothing shipped turns a photo of arbitrary real objects into structured, refereed, screen-light play, offline.
Build in 3h:                  index.html client-side (MediaPipe Gemma multimodal; game-schema constrained JSON: format ∈ race/sort/story/guess, roles, win condition; Web Speech TTS referee + score functions), static deploy. Riskiest 20 minutes: game quality variance — the schema constraint plus 4 hand-tuned format templates keeps output playable.
When the API throttles:       No API. Airplane mode is the opening move of the demo.
Quotable number:              "Screens handed to the kid: 0. Pocket junk to a playable, refereed game: 20 seconds."
Which track it fits:          creative / on-device
Kill risk:                    Judges file it under "toy, not tool." Counter is the frequency argument (this is a daily parenting emergency) — it must be pitched as respite infrastructure, not whimsy.
```

```
IDEA 7 — Three Piles
Problem in one sentence (a person's words, not a market description): "I'm standing over the laundry basket guessing what can go in together and which dial number won't shrink the jumper."
Who and how often:            Households run 2-5 washes a week (JUDGEMENT: standard UK household laundry cadence); the sort-and-settings guess happens before every load.
The 90-second wow:            A real pile of clothes on the table; the judge throws their own jumper on top. ONE photo of the whole pile → three piles on screen, item by item, with the judge's jumper placed and flagged if it conflicts ("red hoodie will dye pile 2"). Then one photo of our actual washing machine's dial → per-pile settings in that machine's own dial positions. Wifi is off the whole time.
Google feature named out loud: Gemma 4 multimodal on-device: it must parse a cluttered many-object photo AND a machine control dial locally, instantly, in a utility room with no signal.
Closest existing thing:       Garma – Clothing Label Scanner (per-garment scan, sorts into wash groups) https://play.google.com/store/apps/details?id=com.stringcode.garma ; Laundry Master https://apps.apple.com/us/app/laundry-master-care-label/id6756978100 — Delta: whole-pile single photo instead of scanning garments one at a time, conflict flagging, and translation to YOUR machine's actual dial from a photo of it — plus offline. Honest note: this is the most crowded prior-art field of my eight.
Build in 3h:                  index.html client-side (two-photo flow, Gemma multimodal, pile UI), static deploy. Riskiest 20 minutes: per-item recognition in one cluttered pile photo — fallback: "3-4 items per photo" batches, which still beats Garma's one-at-a-time.
When the API throttles:       No API in the golden path.
Quotable number:              "20 minutes of sorting and label-squinting → one photo. Ruined loads: 0."
Which track it fits:          on-device / productivity
Kill risk:                    A judge finds Garma on the Play Store during judging and the delta ("whole pile, your dial, offline") sounds like a feature list rather than a product. Weakest novelty of my top seven.
```

```
IDEA 8 — Plain Words
Problem in one sentence (a person's words, not a market description): "The mechanic is telling me what's wrong with my car and I'm nodding while understanding nothing and agreeing to pay for it."
Who and how often:            Jargon-asymmetric conversations — mechanic, letting agent, broadband support, builder — hit an ordinary adult roughly 1-2x/week. Honest flag: that is BELOW the brief's multiple-times-a-week bar; this is the weakest frequency claim of my eight.
The 90-second wow:            A teammate plays the mechanic, live: "Your nearside CV boot's split and the gaiter's gone — want me to do the track rod ends while I'm in there?" As they speak, the judge watches a sidebar render plain English in real time ("a rubber cover on a front axle joint is torn — cheap part, labour is the cost") plus one suggested question ("ask: is the joint itself damaged, or just the cover?"). Judge can then speak any jargon they know at it.
Google feature named out loud: Gemma 4 on-device streaming via LiteRT — recording another person's speech must never touch a cloud, and the translation must keep up with talking pace; a privacy-preserving live interpreter is only possible on-device.
Closest existing thing:       Jargon (Chrome extension, translates written text) https://chromewebstore.google.com/detail/jargon/lddfcbcbmolobdpoddaghdkdkocdinje ; Google Live Translate (languages, not registers) https://support.google.com/translate/answer/6142474 — Delta: live spoken consumer-jargon interpretation with suggested questions, on-device; nothing shipped does the spoken register-translation case.
Build in 3h:                  index.html (Web Speech API push-to-talk chunks → local Gemma → sidebar stream), static deploy. Riskiest 20 minutes: ASR accuracy on jargon in a noisy demo room — push-to-talk chunking and a close mic, not open-mic streaming.
When the API throttles:       No API in the golden path.
Quotable number:              "Times you stop them to ask what that means: 0. Understanding: all of it."
Which track it fits:          on-device / accessibility
Kill risk:                    Noisy-room speech recognition mangles the jargon before the model ever sees it, and the frequency claim is soft under judge questioning. Ranked last for both reasons.
```

---

## Ranking, best first

1. **Second Look** — the only idea here whose wow is a visibly agentic multi-step research chain on judge-supplied input; aimed square at the Gemini 3.7 Flash keynote, with a real (checked) gap: buyer-side, platform-agnostic, in-person.
2. **Doormat** — the best frequency claim of the eight and the cleanest both-keynotes hybrid (private local read, cloud verification); must open with the router unplugged or it pattern-matches to document-AI.
3. **Overshare Check** — safety track + on-device keynote, and the venue itself (badges, whiteboards, screens) is the demo; prior art (Lookr) is closest of the top three, the inference-narration delta must carry it.
4. **Which Button** — genuinely unmined (searches surfaced nothing on point), unfakeable live demo on the venue's own machine; hallucination on obscure panels is the honest worry.
5. **Big Font** — strongest emotional pitch and trivially buildable; ranked mid because the delta is framing (helper-side artifacts) rather than capability, and it lives or dies on print polish.
6. **Backseat Games** — most charming, purest Gemma-keynote demo (multimodal + local function calling, airplane mode), but risks the "toy" label with a technical-execution-weighted rubric.
7. **Three Piles** — great tactile demo, weakest novelty: Garma is uncomfortably close; keep only if the track announcement rewards on-device/home and the top picks don't fit.
8. **Plain Words** — real gap and a fun demo, but the frequency claim is honestly below the brief's bar and live ASR in a demo hall is a coin flip. Cut first.
