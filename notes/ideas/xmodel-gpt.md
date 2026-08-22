<!-- Source: Codex CLI / GPT-5.6, model-generated independent idea list. Command: codex exec -C <repo_root> -s workspace-write -->

```
IDEA 1 — ContextCrop
Problem in one sentence (a person's words, not a market description): I need to send this screenshot, but I do not want the rest of my screen going with it.
Who and how often:            Adults who share chats, tickets, maps, or confirmations 4-12 times a week; those screenshots often contain unrelated names, tabs, and earlier messages.
The 90-second wow:            The judge pastes a fresh screenshot and says, "Show my flatmate only the train delay." The app cuts it to the smallest useful region, masks stray identifiers, and toggles between the original and exactly what the flatmate receives.
Google feature named out loud: Gemma 4 E2B multimodal through LiteRT; the original image is private, and selecting the minimum sufficient context needs layout and intent reasoning on the device.
Closest existing thing:       Snagit Smart Redact https://www.techsmith.com/snagit/features/smart-redact/ — Delta: Snagit finds fixed classes of private data on the existing canvas; ContextCrop uses the named recipient and purpose to remove every region that is not needed for that share.
Build in 3h:                  `index.html`, `app.js`, `model-worker.js`, `styles.css`; Tesseract.js supplies text boxes, Gemma labels their purpose, Canvas crops and burns in masks, and Firebase Hosting serves the public PWA. The riskiest 20 minutes are mapping model-selected text spans back to pixel boxes.
When the API throttles:       The golden path makes no API call. If the local model cannot load, regex masking plus a draggable crop still exports a reviewed image.
Quotable number:              2 minutes of crop-and-blur work → 8 seconds
Which track it fits:          on-device / safety / productivity
Kill risk:                    One missed name or message destroys trust in the export.
```

```
IDEA 2 — PurposePairs
Problem in one sentence (a person's words, not a market description): I am at the door again and cannot tell which one thing I have forgotten.
Who and how often:            Most adults leave home 7-14 times a week; commutes, exercise, shopping, and weather each introduce a different easy-to-miss companion item.
The 90-second wow:            The judge says any outing, such as "cycling to work in rain," and lays out whatever they planned to take. The camera inventories it, checks public weather, and draws one empty glowing outline for the missing companion, such as a helmet or waterproof layer.
Google feature named out loud: Gemini 3.7 Flash agentic tool use; it must read the scene, call public weather and route tools, build an outing-specific dependency graph, and choose one omission rather than dump a packing list.
Closest existing thing:       Alba photo packing https://withalba.app/guides/scan-items-into-bag — Delta: Alba matches a photo against a checklist the user already wrote; PurposePairs has no list and infers one conditional companion from the outing and current conditions.
Build in 3h:                  `app.py`, `tools.py`, `templates/index.html`, `static/app.js`, `Dockerfile`; FastAPI, Gemini structured function calls, Open-Meteo, and Cloud Run with unauthenticated access. The riskiest 20 minutes are forcing a stable one-item answer from a noisy object inventory.
When the API throttles:       One cloud call covers the whole run; after a 429, Gemma 4 ranks a small local dependency table and asks the user to state the weather instead of fetching it.
Quotable number:              90 seconds of doorway rechecking → 10 seconds
Which track it fits:          agents / on-device / productivity
Kill risk:                    If the missing item feels obvious or arbitrary, this looks like a packing checklist with extra steps.
```

```
IDEA 3 — Packet Cross-Exam
Problem in one sentence (a person's words, not a market description): The front of this packet makes a claim, and I cannot see what on the back supports it.
Who and how often:            Grocery and household shoppers face 5-15 packaged-product decisions a week; front claims and the figures or ingredient order that qualify them sit on different sides.
The 90-second wow:            The judge hands over any packet, photographs both sides, and taps one printed claim. Evidence threads join that phrase to the exact back-label lines and return "supported," "conflicts," or "not computable" without issuing a health or legal verdict.
Google feature named out loud: Gemini 3.7 Flash multimodal function calling; it links two views, calls OCR, unit-normalisation, and arithmetic tools, and must refuse a conclusion when the printed evidence is insufficient.
Closest existing thing:       Yuka https://yuka.io/en/app/ — Delta: Yuka scans a barcode and assigns a health score; Packet Cross-Exam tests one user-selected front-of-pack statement only against evidence printed on that same physical packet, with no product rating or advice.
Build in 3h:                  `app.py`, `claim_tools.py`, `templates/index.html`, `static/camera.js`, `Dockerfile`; FastAPI, Gemini vision, deterministic Python arithmetic, and public Cloud Run. The riskiest 20 minutes are preserving coordinates from two OCR passes so every conclusion has a visible evidence line.
When the API throttles:       The app stores OCR after the first call; deterministic arithmetic still handles numeric claims, while local Gemma performs literal evidence matching and returns "not computable" for anything uncertain.
Quotable number:              3 minutes hunting across a label → 12 seconds to cited evidence
Which track it fits:          agents / productivity / safety
Kill risk:                    Most marketing phrases may be too vague to test, leaving the stage demo stuck on "not computable."
```

```
IDEA 4 — Watchword
Problem in one sentence (a person's words, not a market description): I do not need a security camera; I need my phone to watch this one thing for ten minutes.
Who and how often:            Adults wait on visible state changes 5-12 times a week, including a printer finishing, an oven preheat light switching off, a washing cycle ending, or a person reaching a pickup point.
The 90-second wow:            The judge points the camera at two cups and says, "Ring when the red cup moves behind the blue one." They move it in any way they choose, and the alarm fires in airplane mode; the session then deletes itself.
Google feature named out loud: Gemma 4 E2B multimodal through LiteRT; arbitrary visual conditions need semantic comparison across frames, while on-device inference keeps a temporary camera watch private and independent of wifi.
Closest existing thing:       SwannShield Notify Me When https://support.swann.com/hc/en-us/articles/51198444423833-SwannShield-Notify-Me-When-How-It-Works — Delta: Swann saves custom prompts on compatible security cameras; Watchword is a disposable, offline foreground alarm on any phone, with no account, recording, or persistent surveillance setup.
Build in 3h:                  `index.html`, `app.js`, `vision-worker.js`, `manifest.json`; a 1 fps LiteRT loop, Web Notifications, IndexedDB expiry, and Firebase Hosting. The riskiest 20 minutes are keeping local inference fast enough to catch a short transition without overheating the device.
When the API throttles:       No API is used. On weak hardware, a local motion-and-colour detector handles simple triggers and labels the result as reduced mode.
Quotable number:              10 minutes of repeated glances → 10 seconds of setup
Which track it fits:          on-device / accessibility / productivity
Kill risk:                    Venue hardware may run Gemma too slowly for the alarm to feel immediate.
```

```
IDEA 5 — QueueCue
Problem in one sentence (a person's words, not a market description): The shorter line always seems to be the slower one.
Who and how often:            Adults choose between queues 3-8 times a week at cafés, supermarkets, station barriers, toilets, and venue entrances; line length hides service speed.
The 90-second wow:            The judge records an eight-second pan across two improvised live queues. QueueCue picks the faster line and overlays its evidence, such as "three completions here, one there, and a stalled payment," even when that line is longer.
Google feature named out loud: Gemini 3.7 Flash multimodal tool use; it calls a frame sampler, tracker, event counter, and stopwatch, then reasons about completed service events rather than counting heads in one image.
Closest existing thing:       Google Maps Popular Times and wait times https://support.google.com/business/answer/6263531?hl=en — Delta: Maps estimates venue-level busyness from aggregated history; QueueCue compares two uninstrumented lines already in front of the user from one short clip.
Build in 3h:                  `app.py`, `queue_tools.py`, `templates/index.html`, `static/record.js`, `Dockerfile`; FastAPI, OpenCV frame sampling, Gemini structured output, and public Cloud Run. The riskiest 20 minutes are keeping person and service-completion identities consistent across frames.
When the API throttles:       Local tracking still divides observed departures by eight seconds and shows a low-confidence rate; only the semantic explanation disappears.
Quotable number:              5 minutes lost in the wrong line → 8 seconds to choose
Which track it fits:          agents / productivity / accessibility
Kill risk:                    Occlusion in a real crowd can make the event count confidently wrong.
```

```
IDEA 6 — RelayMark
Problem in one sentence (a person's words, not a market description): I can see the thing in the photo, but telling someone where it is takes longer than getting it myself.
Who and how often:            People in shared homes answer "where is it?" 3-6 times a week for chargers, scissors, spices, keys, and remote controls; the useful answer is usually a landmark, not an inventory record.
The 90-second wow:            The judge circles any object in a cluttered camera view. A second judge scans a QR code, sees no room photo, follows one sentence of landmark directions, and finds the object.
Google feature named out loud: Gemma 4 E2B on-device multimodal; it must turn a selected pixel region into relative spatial language while keeping the private room image on the first device.
Closest existing thing:       SnapFind https://www.snapfind.app/ — Delta: SnapFind requires a stored, labelled home inventory; RelayMark creates one-off landmark directions from a single photo, shares text only, and keeps no catalogue.
Build in 3h:                  `index.html`, `app.js`, `model-worker.js`, `qr.js`; Canvas selection, Gemma through LiteRT, and a QR containing the short direction let Firebase Hosting serve the whole public app. The riskiest 20 minutes are grounding the circled pixels to stable left/right/inside/behind relations.
When the API throttles:       No API or server is required because the QR encodes the local model's text. A manual landmark tap remains available if inference fails.
Quotable number:              2 minutes of photo messages → one 15-second direction
Which track it fits:          on-device / productivity / accessibility
Kill risk:                    A vague landmark sentence sends the recipient searching anyway.
```

```
IDEA 7 — Handoff Pin
Problem in one sentence (a person's words, not a market description): I need to show the next person where I stopped without writing an essay.
Who and how often:            Adults sharing a home or caring for family hand off 4-10 unfinished chores, collections, deliveries, or preparations a week; raw photos and voice notes bury the one unresolved step.
The 90-second wow:            One judge pauses a tabletop task, snaps it, and says what has happened. Gemini visibly calls "crop evidence," "separate done from open," and "mint 20-minute link"; a second judge opens the QR and gets one evidence crop plus one next action.
Google feature named out loud: Gemini 3.7 Flash agentic function calling; the point is the visible tool chain that reduces messy scene-plus-speech input to a scoped, expiring handoff rather than composing a summary.
Closest existing thing:       didit https://didit.ai/ — Delta: didit turns a photo or description into a shared task list; Handoff Pin captures an already-part-finished physical state, retains one evidence crop, and passes on only the sender-confirmed unresolved step through an expiring link.
Build in 3h:                  `app.py`, `handoff_tools.py`, `templates/index.html`, `static/capture.js`, `Dockerfile`; FastAPI, Gemini tool calls, SQLite TTL rows, QR generation, and public Cloud Run. The riskiest 20 minutes are preventing the model from inventing a next step that the sender never stated.
When the API throttles:       A single retry falls back to local Gemma extraction; if that also fails, the sender manually selects the evidence crop and records the one next action before the link is created.
Quotable number:              4-minute household handover → 20 seconds
Which track it fits:          agents / productivity
Kill risk:                    One invented state change creates more confusion than the original photo.
```

```
IDEA 8 — Parcel Proofreader
Problem in one sentence (a person's words, not a market description): I opened the bag, but I still have to compare every tiny variant and included part with what I ordered.
Who and how often:            Online-grocery and click-and-collect users check 3-8 delivered bags, parcels, substitutions, or collected items a week; even correct handoffs need a quick line-by-line check.
The 90-second wow:            The judge supplies any listing screenshot and a real object or bag. The app boxes the visible item, crosses off exact matches, and points to one wrong colour, size, quantity, or missing included part without logging into a shop.
Google feature named out loud: Gemini 3.7 Flash multimodal function calling; it extracts an order schema from one image, an observed-item schema from another, and calls a deterministic diff tool instead of asking one model for a loose visual verdict.
Closest existing thing:       Intelgic shipment verification https://intelgic.com/ai-product-identification-verification — Delta: Intelgic checks outbound goods against purchase orders on an industrial packing line; Parcel Proofreader gives the recipient the reverse check from two phone images, with no retailer integration or fixed camera.
Build in 3h:                  `app.py`, `diff_tools.py`, `templates/index.html`, `static/camera.js`, `Dockerfile`; FastAPI, two Gemini structured extractions, a Python schema diff, and public Cloud Run. The riskiest 20 minutes are making "not visible" win over a guessed match for hidden attributes.
When the API throttles:       OCR and barcode reads run locally, Gemma 4 compares visible text and colour, and hidden attributes stay marked unknown; the app never turns missing evidence into a pass.
Quotable number:              4 minutes checking a multi-item handoff → 15 seconds
Which track it fits:          agents / on-device / productivity
Kill risk:                    A stage object with no visible model or variant cues produces an honest but unimpressive wall of unknowns.
```

RANKED BEST FIRST
1. ContextCrop: the judge supplies genuinely private input, the local-only story is obvious, and the one missed-redaction risk is easy to explain and review.
2. PurposePairs: it makes agentic tool use visible in a daily ritual, though the inferred omission must feel smarter than a checklist.
3. Packet Cross-Exam: the evidence threads make reasoning legible in seconds, but a poor packet choice can yield only "not computable."
4. Watchword: airplane-mode semantic triggering is a clean keynote demo, but nearby security-camera products make the disposable local delta carry the novelty claim.
5. QueueCue: it has the freshest interaction and a strong live challenge, offset by the highest vision-reliability risk.
6. RelayMark: the text-only privacy reveal is memorable and small enough to finish, though spatial wording can be flaky.
7. Handoff Pin: the expiring evidence card is useful and agentic, but judges may see it as structured messaging unless the tool chain lands cleanly.
8. Parcel Proofreader: the schema diff is technically honest and buildable, but ordinary-use frequency is weaker and hidden attributes can flatten the demo.
