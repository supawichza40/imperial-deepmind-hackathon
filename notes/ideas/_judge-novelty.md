# Novelty judge — all 56 ideas, scored cold

Judge: independent, no authorship stake. Read the brief (`notes/plans/2026-08-22-cross-model-prompt.md`)
and all 10 idea files. Scored 0–5 on **genuine novelty only** (not buildability, not frequency).
Rubric: 5 = nothing shipped does this, closest thing is a different job · 3 = adjacent products
shipped, the specific move is new · 1 = a shipped product does substantially this · 0 = platform-native
or template. ~20 load-bearing prior-art claims were re-verified by fresh web search (marked ✓);
the rest judged against the files' own admissions plus known market. Scout self-reported prior art
was **not** taken on trust — four scout #1-ranked picks died on re-check.

## Cross-model convergence (independent runs, no shared context)

1. **Which Button (fable) ≡ Appliance Control Panel Decoder (home-food)** — same idea, twice,
   independently. Prior-art check comes back clean ✓ (only OEM smart-appliance apps exist, nothing
   points-camera-at-any-panel). Real signal — and a warning that other teams can land here too.
   Keep **Which Button** (offline, any machine, venue-demo-able); kill the duplicate.
2. **Doormat (fable) ≡ Deadline Priority Inbox (money-admin)** — same pile-of-letters triage. Both
   damaged: letter-scan-to-deadline is a shipped category ✓ (LetterMagic, Papeer, MailScan AI,
   PaperAI). money-admin claimed "cleanest whitespace in the whole search" — false. Fable at least
   cited the prior art honestly.
3. **Three Piles (fable) ≡ Laundry Pile Sorter (home-food)** — same idea; Garma already ships
   photo→wash-group sorting. Both die.
4. **Scam-detection triad** — Is This Real? (inbox) ≡ Scam/Fake Bill Detector (money) ≡ Scam
   Screenshot Triage (phone-a11y, already self-killed). Three domains converged on a category that
   is saturated *including the on-device delta*: Gemma Guard is an existing open-source
   screenshot→on-device-Gemma→verdict project from a previous Gemma hackathon. All dead.
5. **Plain Words (fable) ~ Plain-Language Simplifier (phone-a11y)** — same accessibility instinct,
   different modality. Written-text simplification is shipped 3× over (Immersive Reader, Google
   "Simplify", Vite Vere — a Gemma-prize winner); **live spoken** register translation is not. Keep
   Plain Words only.
6. **Decision Archaeologist (work) ~ Group Chat Unstick (inbox)** — same mechanism (paste thread →
   decision state), different corpus. Both sit on shipped summarizers; both die.

## Scores

| Idea | Source file | Nov. | Closest shipped thing I found | Verdict |
|---|---|:-:|---|---|
| Deadline Priority Inbox | money-admin.md | 1 | ✓ [Papeer](https://papeer.ai/) + [LetterMagic](https://play.google.com/store/apps/details?id=com.builtbyboard.Lettermagicfrontend) — scan letters → deadlines, notifications, drafted replies | KILL — the "no direct shipped match" claim is false; ranking-across-a-pile is a feature on a shipped category |
| Owed Money Message Coach | money-admin.md | 2 | Splitwise reminders + the sea of AI message-tone drafters (Rizz-class apps) | KILL — "AI drafts the awkward message" is template-adjacent; escalation ladder is prompt garnish |
| Renewal Ambush Negotiator | money-admin.md | 2 | Rocket Money / Trim bill negotiation; UK [Nous.co](https://www.nous.co/) handles renewal hikes end-to-end | KILL — negotiation-on-renewal is a funded shipped category; photo→script is a wrapper |
| Statement Fee Hunter | money-admin.md | 1 | [Rocket Money](https://rocketmoney.com/) (file admits it) | KILL — no-OAuth paste-in is a demo constraint dressed as a product |
| Scam / Fake Bill Detector | money-admin.md | 1 | [ScamScan](https://apps.apple.com/us/app/scamscan-ai-scam-detector/id6760021038), Scam Scanner (file admits) | KILL — saturated, and 3-way internal convergence proves everyone thinks of it |
| Bottle Cam | health-body.md | 1 | ✓ [Water AI](https://apps.apple.com/us/app/water-ai-smart-hydration/id6757321179) + [WaterFocus](https://apps.apple.com/us/app/water-tracker-ai-waterfocus/id6743394535) — snap photo of any bottle/glass → AI estimates volume, no manual entry | KILL — scout's #1 pick; its "nobody shipped camera fill estimation" claim is flatly false, twice over |
| Symptom Ramble | health-body.md | 1 | ✓ [HealthStory AI](https://start.healthstoryai.com/) (voice → structured symptom record for the GP) + [Migraine Trail](https://migrainetrail.com/) voice logging | KILL — "ramble → structured timeline" is shipped, follow-up questions included |
| Cabinet Sweep | health-body.md | 2 | [ScanMyPills](https://apps.apple.com/us/app/scanmypills-pill-reminder-log/id6754493741) (photo→schedule per bottle) | KILL — batch-vs-per-item is a feature tweak the file itself calls its weakest delta |
| Sleep Ledger, Spoken | health-body.md | 1 | Sleep Ledger: Debt Tracker (file admits ledger is commodity) | KILL — voice skin on a shipped app, same name included |
| Morning-After Plan | health-body.md | 2 | HungRecover (file admits) | KILL — voice skin + templated reminders; weakest frequency in its own file too |
| Cleaning Product Matcher | home-food.md | 4 | ✓ nothing shipped does photo-your-actual-products → mixing-hazard flag; closest is [CleanBot AI](https://apps.apple.com/us/app/cleanbot-ai-stain-solution/id6758080832) (generic stain advice) + static safety pages | KEEP — verified whitespace with a felt safety payoff; watch the hallucinated-hazard risk |
| Appliance Control Panel Decoder | home-food.md | 4 | ✓ clean (only OEM smart-appliance apps, e.g. Samsung AI Control — different job) | KILL as duplicate — same idea as Which Button, which executes it better (offline, any machine) |
| Laundry Pile Sorter | home-food.md | 2 | [Garma](https://play.google.com/store/apps/details?id=com.stringcode.garma) sorts garments into wash groups | KILL — pile-batch vs per-garment is a thin delta on a shipped app |
| Bin Whisperer | home-food.md | 1 | [West Northants council app](https://www.westnorthants.gov.uk/news/enhanced-app-launched-make-everyday-services-easier) photo→bin guidance (file admits) | KILL — a UK council literally ships it |
| Grocery Shelf Duplicate-Buy Preventer | home-food.md | 2 | NoWaste / Fridgely pantry-inventory category | KILL — stateless-photo wedge on a crowded category; file ranks it last itself |
| Is This Real? | inbox-comms.md | 1 | Fishy, ScamScan, Norton Genie; **on-device delta pre-empted by Gemma Guard** (open-source screenshot→local-Gemma scam verdict from a prior Gemma hackathon, per phone-a11y's own kill log) | KILL — scout's #1; even the "we run locally" line has been done, at a Gemma event no less |
| Get Me A Human | inbox-comms.md | 3 | [GetHuman](https://gethuman.com/) (crowdsourced DB) + ✓ B2B IVR-tree mappers ([VoiceInfra](https://voiceinfra.ai/features/ivr-detection) "traverses the tree, calculates shortest path"; Retell, Vapi) | KEEP (weak) — consumer paste-in wedge is real but the mechanism is shipped B2B infrastructure |
| Voicemail Triage | inbox-comms.md | 2 | YouMail / Pixel Call Screening (transcript + scam flag, file admits commodity) | KILL — callback-script layer is prompt garnish on a shipped core |
| Group Chat Unstick | inbox-comms.md | 1 | [GistGem](https://chromewebstore.google.com/detail/gistgem-whatsapp-group-ch/pdeglbcbdehfjfllclngapefcppbbjmp), ThreadRecap (file admits) | KILL — chat-summariser template with a nudge button |
| Actually, When? | inbox-comms.md | 3 | When2meet (different job); AI email schedulers (Skej/Howie-class, CC-a-bot) need account setup | KEEP (weak) — paste-thread constraint-solving with zero OAuth is a real gap, dull wow |
| Notification Declutter Coach | phone-a11y.md | 1 | [Pixel Notification Organizer / summaries](https://support.google.com/pixelphone/answer/16691280) — Google ships the job natively; Apple prioritizes notifications too | KILL — scout's #1; screenshot-audit of your own notification shade is a workaround, not a product |
| Dark Pattern X-Ray | phone-a11y.md | 2 | ✓ screenshot-upload dark-pattern detectors exist ([YesChat GPT](https://www.yeschat.ai/gpts-9t557DT3dkO-Dark-Pattern-Detector), Fair Patterns, Devpost NB extension, academic frameworks) | KILL — mined space; "where to tap" instruction is the only sliver left |
| Doomscroll Mirror | phone-a11y.md | 3 | BloomScroller (Devpost), Opal/One Sec (real-time interruption — different job) | KEEP (weak) — the retrospective causal one-liner is new, but unverifiable subjective output is a novelty that can't prove itself on stage |
| Plain-Language Live Simplifier | phone-a11y.md | 1 | Microsoft Immersive Reader; Google app "Simplify"; Vite Vere (Kaggle Gemma prize winner — same lane) | KILL — the judges' own ecosystem already awarded this idea |
| Tab Triage | phone-a11y.md | 1 | ✓ [TabBrew](https://chromewebstore.google.com/detail/tabbrew-%E2%80%93-ai-tab-manager/ikmpmkkcmhhnjmdiooekbhfmomcbefkf), AI Tab Master, Tabbit, Tab Reaper + Chrome's native AI tab groups | KILL — flagged unverified by its own scout; verification kills it instantly, category is saturated |
| Blind-Spot Wayfinder | travel-commute.md | 4 | ✓ nothing ships photo-a-posted-station-map → offline Q&A; Citymapper offline = pre-digitized data for ~40 cities (different mechanism) | KEEP — verified whitespace; offline is structural, not bolted on. Novelty survives; execution risk is someone else's problem |
| Which Row's Mine | travel-commute.md | 3 | National Rail / Citymapper own-data feeds; Google Lens finds text but not goal-filtered answers | KEEP (weak) — real gap but feels like a Lens query away from obsolete |
| Cycling Rule Decoder | travel-commute.md | 2 | ParkLens / ClearPark / "Can I Park Here AI" — same photo→sign-verdict move, adjacent sign type (file's own kill log) + DfT reference app | KILL — the move is shipped 3× for parking; changing the sign category isn't novelty |
| Missed-Parcel Slip Decoder | travel-commute.md | 3 | [Parcel Tracker](https://www.parceltracker.com/) (needs courier + barcode — different job) | KEEP (weak) — genuine micro-gap, small product |
| Carry-On Security Checker | travel-commute.md | 1 | ✓ [AirTravel ItemCheck](https://play.google.com/store/apps/details?id=com.coreprec.airtravel) — photo of items → allowed/restricted/prohibited per airline/airport; [OneBag](https://apps.apple.com/us/app/onebag-travel-packing-list/id6761047805) AI Snap & Check | KILL — "no shipped whole-bag-photo scanner found anywhere" is false |
| Spot the Gap | work-learning.md | 4 | ✓ nothing consumer-shipped; closest are prompt-checkers and a USPTO patent on receiver-reaction prediction — not products | KEEP — verified whitespace; simulate-the-recipient is a genuinely fresh interaction, and it demos on judge-supplied text |
| Decision Archaeologist | work-learning.md | 2 | Slack AI recaps; ADR agents | KILL — dissent/open-questions are output fields, not a new product; reads as the banned summariser in 90 seconds |
| Rubber-Duck Handover | work-learning.md | 3 | Standuply, voice-journal apps (BrainFlow) | KEEP (weak) — live targeted interview is a real but narrow delta |
| Jargon Cartographer | work-learning.md | 1 | Google's own [NotebookLM Mind Maps](https://9to5google.com/2025/03/27/notebooklm-mind-map/) | KILL — a variant of the judges' employer's product, presented to the judges' employer |
| Did I Get That Right? | work-learning.md | 3 | Socra, ReExplain (compare vs the AI's general knowledge — different reference) | KEEP (weak) — specific-transcript diff is real; subtle enough to die in a 90-second walk-by |
| CareThread | care-relationships.md | 3 | CareSplit / manual care-log apps; AI-calls-the-senior products are the adjacent hot space | KEEP — ambient sibling-side capture + pattern counts is a real gap in a crowded-adjacent field |
| CheckLine | care-relationships.md | 1 | ✓ [MyndYou](https://www.myndyou.com/) (passively tracks speech-pattern change on calls, alerts carers), [ElderVoice](https://www.eldervoice.com/), [TortoiseAI](https://tortoiseai.xyz/), QuikTok | KILL — "no shipped consumer app at this intersection" is false; the intersection is a funded category |
| Wishline | care-relationships.md | 3 | WishMe / Gifties (deliberate list entry) | KEEP (weak) — passive-capture framing is new; the product under it is a notes app |
| In Their Own Words | care-relationships.md | 4 | HereAfter AI / Seance AI / Dadbot — all **simulation**; nothing ships retrieval-only verbatim grief memory | KEEP — the anti-deadbot design stance is genuinely novel and defensible under Q&A; frequency is weak but that's not this axis |
| CueCard | care-relationships.md | 4 | AAC tools incl. the Kaggle Gemma pictogram winner — all output-facing for the non-verbal person; nothing serves the substitute carer's lookup | KEEP — audience inversion on a real niche, on-device story is honest |
| Second Look | xmodel-fable.md | 2 | ✓ [Underpriced AI](https://underpricedai.com/) — photos OR screenshots from any marketplace → sold comps, deal score, red flags; [Spottable](https://chromewebstore.google.com/detail/spottable-facebook-market/dbgjphnanjmmfjacahfhliahblokmpgh) (deal score, condition, red flags, batch); Price Snap (damage detection) | KILL — Fable's #1; the buyer-vs-reseller framing is the only unshipped sliver and a judge won't credit it |
| Doormat | xmodel-fable.md | 2 | ✓ [LetterMagic](https://lettermagic.app/) / [Papeer](https://papeer.ai/) (scan letters → deadlines + notifications + replies, both cited honestly in-file) | KILL on novelty — wifi-off privacy split is architecture, not a new job; the category is shipped 4× over |
| Overshare Check | xmodel-fable.md | 3 | [Lookr](https://apps.apple.com/in/app/lookr-ai-photo-privacy/id6761846110) (detect+blur classes); metadata scorers (Scanly) | KEEP — inference-chain narration ("what a stranger could DO") is the new move; category is warm, not cold |
| Which Button | xmodel-fable.md | 4 | ✓ clean — Google Lens identifies, doesn't guide; ManualsLib needs model numbers; only OEM apps for smart appliances | KEEP — verified whitespace + independent 2-model convergence; the best-validated novel idea in the pool |
| Big Font | xmodel-fable.md | 3 | Duca / Apo serve the older adult directly; TeamViewer-class = remote control | KEEP — helper-side printable artifact is unshipped; delta is packaging more than capability |
| Backseat Games | xmodel-fable.md | 1 | ✓ [FunDad](https://www.fundad.app/) — camera maps your objects/room → builds a custom kid activity, used in airports and waiting rooms | KILL — "nothing shipped turns a photo of objects into play" is false; offline+referee doesn't save it |
| Three Piles | xmodel-fable.md | 2 | [Garma](https://play.google.com/store/apps/details?id=com.stringcode.garma) (file admits closest) | KILL — duplicate of Laundry Pile Sorter, both under Garma's shadow |
| Plain Words | xmodel-fable.md | 4 | [Jargon extension](https://chromewebstore.google.com/detail/jargon/lddfcbcbmolobdpoddaghdkdkocdinje) (written text); Google Live Translate (languages, not registers) | KEEP — live spoken consumer-jargon interpretation is unshipped; frequency + noisy-room ASR are its real (non-novelty) problems |
| ContextCrop | xmodel-gpt.md | 3 | ✓ auto-redaction is crowded ([ShareGuard](https://apps.apple.com/us/app/shareguard-blur-redact/id6752704315), [Redact Photo](https://apps.apple.com/us/app/redact-photo-censor-blur/id6749859478), Snagit Smart Redact) — all class-based PII detection | KEEP — recipient/purpose-driven *minimum-sufficient-context* cropping is a genuinely different move from PII-class blurring; GPT's #1 survives, damaged |
| PurposePairs | xmodel-gpt.md | 2 | PackPoint (weather-aware packing lists, shipped ~decade) + [Alba](https://withalba.app/guides/scan-items-into-bag) (photo-check against list) | KILL — both halves shipped; "no list, one glowing item" is UX, and GPT's own kill-risk line says it: checklist with extra steps |
| Packet Cross-Exam | xmodel-gpt.md | 3 | ✓ [Label Score AI](https://labelscore.ai/) validates front-of-pack claims against ingredients/nutrition — but B2B compliance for brands; consumer scanners (Yuka, Food Check AI) score, don't verify a chosen claim | KEEP — same mechanism exists B2B; consumer claim-vs-evidence threading is new. "Not computable" demo risk is real |
| Watchword | xmodel-gpt.md | 4 | ✓ AI security cams alert on fixed classes (person/vehicle/animal); nothing ships arbitrary natural-language visual conditions, disposable, offline | KEEP — verified whitespace; "ring when the red cup moves behind the blue one" has no shipped equivalent |
| QueueCue | xmodel-gpt.md | 5 | ✓ nothing found consumer-side; enterprise queue analytics (fixed venue cameras) and Google Maps busyness are different jobs entirely | KEEP — the only 5 in the pool; also one of the highest technical-risk builds, which is not this judge's axis but should scare the lead |
| RelayMark | xmodel-gpt.md | 4 | [SnapFind](https://www.snapfind.app/) (persistent labelled inventory — different job) | KEEP — one-shot landmark-direction relay is unshipped; micro-utility, but genuinely new |
| Handoff Pin | xmodel-gpt.md | 3 | [didit](https://didit.ai/) (photo→task list) | KEEP (weak) — expiring evidence-crop handoff is new-ish; risks reading as structured messaging |
| Parcel Proofreader | xmodel-gpt.md | 4 | [Intelgic](https://intelgic.com/ai-product-identification-verification) (industrial outbound verification — different audience/job) | KEEP — recipient-side order-vs-received diff is unshipped consumer-side; frequency claim is its weak flank |

## Casualty report

- **31 killed / 25 kept.** Four scout **#1-ranked picks died on independent re-check**: Bottle Cam
  (health), Is This Real? (inbox), Notification Declutter Coach (phone-a11y), Second Look (fable),
  plus money-admin's #1 Deadline Priority Inbox. Scout self-verification was systematically
  optimistic — every "cleanest whitespace in the set" claim I could test was wrong except
  work-learning's (Spot the Gap held) and home-food's (Cleaning Product Matcher held).
- The `xmodel-gpt` file had the best survival rate (6/8 kept) — its ideas were odder and less
  template-shaped. The domain scouts over-indexed on "point camera at household object, get
  answer," which is exactly the strip-mined shape.

## Top 8 by novelty

1. **QueueCue** (5, xmodel-gpt) — no shipped product picks the faster of two physical queues from a phone pan; nearest things are different jobs. Highest novelty AND highest vision-risk build.
2. **Watchword** (4, xmodel-gpt) — arbitrary-semantic-condition camera alarm, offline, disposable. Verified: only class-based security cams exist. Pure Gemma-keynote fit.
3. **Which Button** (4, xmodel-fable) — verified clean, and two independent models converged on it. Best-validated novelty in the pool; assume other hackathon teams may also find it.
4. **Spot the Gap** (4, work-learning) — simulate-the-recipient ambiguity detection; verified nothing shipped (patents and prompt-linters only). Cleanest text-only build among the 4s.
5. **Blind-Spot Wayfinder** (4, travel-commute) — photograph the posted station map, ask questions, fully offline; verified unshipped, offline is structural.
6. **Cleaning Product Matcher** (4, home-food) — photo your actual products → cross-product hazard flag; verified whitespace, visceral safety wow.
7. **In Their Own Words** (4, care-relationships) — retrieval-only anti-deadbot memory; the entire shipped category does the opposite. Novel as a design stance, weak on frequency.
8. **Plain Words** (4, xmodel-fable) — live spoken jargon-to-plain-English; unshipped modality (text version exists). Near-misses at 4: CueCard, RelayMark, Parcel Proofreader.
