# Demo-judge scoring — what actually happens in the room

Standing in for a GDM DevRel judge with 90 seconds to 3 minutes at the table, who will
not read any code. I did not generate any of these ideas and I read them cold.

**Scoring frame** (0–5 on stage wow only, not on build quality or market size):

- **+** the judge supplies the input with their own hands, phone, or voice — unrehearsable beats polished
- **+** the payoff lands under ~20 seconds with no setup narration
- **+** it names a thing the judges shipped and presented this morning: Gemini 3.7 Flash agentic tool use (Amit Vadi) or Gemma 4 on-device (Ian Ballantyne). Both = double
- **+** the judge can repeat it to the next judge without notes
- **+** it survives venue wifi, or is better offline
- **−** the flow only reads as impressive if you already understand the problem
- **−** the payoff is a block of prose that looks like a chatbot answer
- **−** anything needing a caveat before the payoff lands
- **−** the interesting part is invisible

Two facts I applied to every score, because a judge experiences them and a spec sheet
does not:

1. **`notes/MEASURED-on-device-reality.md`, status `observed`:** Gemma 4 on this team's
   M1 runs at **4.74 tok/s with a 65-second cold load**. Every "8 seconds, offline"
   claim in this corpus is *unverified*. That does not kill the on-device ideas — it
   means the on-device wow must be a **short label or a binary event**, never generated
   prose, and the model must be pre-warmed before the judge walks up.
2. **`docs/10-tracks-rules-rubric.md` (announced 12:30, authoritative):** three tracks,
   three separate £400 prizes. Track choice is a competitive decision. Presentation &
   Live Demo is 20% of the score and explicitly includes **demo reliability**.

---

## All 56 ideas

| # | Idea | Source | Wow | What the judge physically does | Input |
|---|---|---|---|---|---|
| 1 | Overshare Check | xmodel-fable.md | **5** | Takes one photo of where they're standing, in airplane mode | judge-supplied |
| 2 | Doormat | xmodel-fable.md | **4** | Watches the wifi go off, pulls a letter out of their own bag | judge-supplied |
| 3 | Second Look | xmodel-fable.md | **4** | Screenshots any live marketplace listing off their own phone | judge-supplied |
| 4 | Which Button | xmodel-fable.md | **4** | Walks to the venue's own coffee machine and names a goal | judge-supplied |
| 5 | Get Me A Human | inbox-comms.md | **4** | Invents the worst phone menu they can, out loud | judge-supplied |
| 6 | Watchword | xmodel-gpt.md | **4** | Invents a trigger condition, then performs it with their hands | judge-supplied |
| 7 | Is This Real? | inbox-comms.md | **4** | Pastes a real scam text off their own phone, then kills the wifi | judge-supplied |
| 8 | Bottle Cam | health-body.md | **4** | Hands over their own water bottle at whatever level it's at | judge-supplied |
| 9 | Big Font | xmodel-fable.md | 3 | Screenshots their own phone, receives a printed A4 | judge-supplied (needs a printer) |
| 10 | Backseat Games | xmodel-fable.md | 3 | Empties their pockets onto the table | judge-supplied |
| 11 | Three Piles | xmodel-fable.md | 3 | Throws their own jumper onto a laundry pile | judge-supplied |
| 12 | Packet Cross-Exam | xmodel-gpt.md | 3 | Hands over any packet, taps one printed claim | judge-supplied |
| 13 | PurposePairs | xmodel-gpt.md | 3 | Names an outing, lays out what they'd take | judge-supplied |
| 14 | ContextCrop | xmodel-gpt.md | 3 | Pastes a fresh screenshot, names who it's for | judge-supplied |
| 15 | RelayMark | xmodel-gpt.md | 3 | Circles an object; a second judge scans a QR and finds it | judge-supplied, needs 2 people |
| 16 | Carry-On Security Checker | travel-commute.md | 3 | Empties pockets and bag, one photo of the pile | judge-supplied |
| 17 | Bin Whisperer | home-food.md | 3 | Hands over a real piece of rubbish | judge-supplied |
| 18 | Blind-Spot Wayfinder | travel-commute.md | 3 | Watches airplane mode go on, photographs a station map | judge-supplied |
| 19 | Which Row's Mine | travel-commute.md | 3 | Names a destination against a busy departure-board photo | judge-supplied |
| 20 | Dark Pattern X-Ray | phone-a11y.md | 3 | Screenshots any confusing cancel/cookie page in the room | judge-supplied |
| 21 | Notification Declutter Coach | phone-a11y.md | 3 | Screenshots their own lock screen | judge-supplied |
| 22 | Spot the Gap | work-learning.md | 3 | Pastes a real instruction they actually sent someone | judge-supplied |
| 23 | Appliance Control Panel Decoder | home-food.md | 3 | Points a phone at a panel and states a goal | judge-supplied |
| 24 | Laundry Pile Sorter | home-food.md | 3 | Watches a photographed pile split into three | rehearsed props |
| 25 | Cabinet Sweep | health-body.md | 3 | Lays out 3–4 pill bottles, one photo | rehearsed props |
| 26 | Symptom Ramble | health-body.md | 3 | Rambles into a mic for 20 seconds | judge-supplied |
| 27 | Voicemail Triage | inbox-comms.md | 3 | Records a fake voicemail into the mic | judge-supplied |
| 28 | Deadline Priority Inbox | money-admin.md | 3 | Hands over 3–4 bills, watches one ranked list appear | mixed |
| 29 | Renewal Ambush Negotiator | money-admin.md | 3 | Reads the generated phone script out loud | rehearsed input |
| 30 | Statement Fee Hunter | money-admin.md | 3 | Dictates three fake charges, sees the monthly total | judge-supplied |
| 31 | Scam / Fake Bill Detector | money-admin.md | 3 | Photographs a staged fake letter | rehearsed |
| 32 | Wishline | care-relationships.md | 3 | Says a wish out loud, then asks for it back | judge-supplied, seeded history |
| 33 | Cleaning Product Matcher | home-food.md | 2 | Points a camera at a staged product pair | rehearsed (judge input barred from the safety half) |
| 34 | Grocery Shelf Duplicate-Buy | home-food.md | 2 | Says an item name at a staged shelf photo | mixed |
| 35 | Cycling Rule Decoder | travel-commute.md | 2 | Asks "can I ride here" at a sign photo | rehearsed |
| 36 | Missed-Parcel Slip Decoder | travel-commute.md | 2 | Holds up a delivery card | rehearsed |
| 37 | Doomscroll Mirror | phone-a11y.md | 2 | Screenshots their own screen-time page | judge-supplied |
| 38 | Plain-Language Live Simplifier | phone-a11y.md | 2 | Points a camera at dense text | judge-supplied |
| 39 | Tab Triage | phone-a11y.md | 2 | Screenshots their tab switcher | judge-supplied |
| 40 | Group Chat Unstick | inbox-comms.md | 2 | Pastes a sample group chat | rehearsed |
| 41 | Actually, When? | inbox-comms.md | 2 | Pastes a messy scheduling thread | rehearsed |
| 42 | Owed Money Message Coach | money-admin.md | 2 | Says a made-up debt scenario out loud | judge-supplied |
| 43 | Sleep Ledger, Spoken | health-body.md | 2 | Describes a made-up night's sleep | judge-supplied |
| 44 | Decision Archaeologist | work-learning.md | 2 | Pastes a long thread | judge-supplied |
| 45 | Rubber-Duck Handover | work-learning.md | 2 | Talks for 60–90s about their own work | judge-supplied (eats the whole window) |
| 46 | Jargon Cartographer | work-learning.md | 2 | Pastes a jargon-heavy message, watches a graph draw | judge-supplied |
| 47 | Did I Get That Right? | work-learning.md | 2 | Listens, then paraphrases back | needs 2 people |
| 48 | CareThread | care-relationships.md | 2 | Speaks a care note while holding a pill bottle | judge-supplied input, seeded history |
| 49 | CheckLine | care-relationships.md | 2 | Records a check-in against pre-seeded weeks | rehearsed |
| 50 | QueueCue | xmodel-gpt.md | 2 | Records an 8-second pan across improvised queues | staged |
| 51 | Handoff Pin | xmodel-gpt.md | 2 | Pauses a tabletop task, hands a QR to a second judge | rehearsed |
| 52 | Parcel Proofreader | xmodel-gpt.md | 2 | Holds up an object plus a listing screenshot | judge-supplied |
| 53 | Plain Words | xmodel-fable.md | 2 | Speaks jargon at a mic in a noisy hall | judge-supplied |
| 54 | Morning-After Plan | health-body.md | 1 | Describes a night out | judge-supplied |
| 55 | In Their Own Words | care-relationships.md | 1 | Asks a question of a seeded quote archive | rehearsed |
| 56 | CueCard | care-relationships.md | 1 | Types an observed cue against a seeded glossary | rehearsed |

---

# Top 5 — beat by beat

## 1. Overshare Check — wow 5

`xmodel-fable.md`, idea 3. **Track 2 (Best Use of Gemma).**

The only idea in the corpus where the venue itself is the demo. This room is full of
lanyards, badges, laptop screens and whiteboards. A photo taken anywhere in it will hit.
And the finding is about the judge personally, which is why they will repeat it.

**Opening sentence:** "Put your phone in airplane mode and take a photo of wherever
you're standing — I want to show you what a stranger would learn from it."

**The 90 seconds:**

| Time | Beat |
|---|---|
| 0:00–0:08 | Presenter turns airplane mode on **in front of the judge**, holds up the phone so the icon is visible. Opening sentence. |
| 0:08–0:15 | Judge takes one photo — themselves, the table, the whiteboard, whatever they choose. |
| 0:15–0:28 | Screen: "Reading locally. No network." Airplane icon stays on screen the whole time. |
| 0:28–0:50 | Four findings appear one at a time, each as an inference chain, not a label: "Badge, bottom left → your full name and employer." "Whiteboard → the venue wifi password." "Screen behind you → an open inbox, three sender names readable." "Lanyard colour → you're on the public attendee list." |
| 0:50–1:00 | One tap. All four regions blur. Before/after toggle, twice. |
| 1:00–1:12 | "The wifi never came back on. Nothing you just photographed left this phone." |
| 1:12–1:30 | The number, then one line: next step is the share-sheet extension. |

**The quotable number:** *"A photo you'd have posted without a second thought → four
things a stranger could learn about you, caught before you post, with the network off."*

Measure the real seconds at 16:00 and put the true figure in. Do not say "8 seconds"
until a stopwatch says so.

**Most likely to fail live:** the on-device call. Two ways — a 65-second cold load if the
model wasn't pre-warmed, or a false negative where it misses the badge the judge is
literally wearing and the table laughs. Third way, specific to Fable's build note:
in-browser MediaPipe Gemma 4 multimodal over WebGPU may simply not load on the demo
machine.

**Fallback:** (a) pre-warm the model before every judge approach — a warm-loop script,
never a cold load on stage; (b) cap output at four short findings with thinking tokens
suppressed, per the measured-reality doc's own guidance; (c) a `DEMO_OFFLINE` cache
keyed on one rehearsed venue photo that serves if the local call passes 12 seconds;
(d) a 40-second screen recording of a genuine judge-style run, shot by 16:30 with the
identical script, so switching to it reads as deliberate. Never claim exhaustiveness —
say "here's what I can see so far", which makes a miss a limit rather than a failure.

---

## 2. Doormat — wow 4

`xmodel-fable.md`, idea 2. **Track 3 (Hybrid) — the cleanest hybrid story in the corpus.**

The router being unplugged is theatre a judge can retell in one sentence. And it is the
only idea here where using both keynote features is the *architecture* rather than a
feature list: Gemma reads the private letter locally, Gemini verifies the non-sensitive
extract against the real gov.uk page.

**Opening sentence:** "I'm going to turn the wifi off — and then I'd like you to hand me
the most boring letter in your bag."

**The 90 seconds:**

| Time | Beat |
|---|---|
| 0:00–0:06 | Presenter kills the wifi visibly. Opening sentence. |
| 0:06–0:20 | Judge picks a letter — their own, or any one from the team's stack of eight real ones. **They choose which**, which is what keeps it unrehearsable. |
| 0:20–0:35 | The letter lands on a triage board: **ACT BY 5 SEP / FILE / BIN / SCAM?** with the deadline and the amount pulled out. |
| 0:35–0:55 | Two more letters, fast. Board fills. "None of these left this laptop." |
| 0:55–1:08 | Wifi back on. The enrich column verifies one deadline against the live gov.uk page — visibly a second, different model doing a second, different job. |
| 1:08–1:20 | One tap → `.ics` file → opens in the judge's own calendar. No login, no account. |
| 1:20–1:30 | The number. |

**The quotable number:** *"A week of doormat pile — 20 minutes of dread and re-reading →
a triage board in 90 seconds, and the NHS letter never left the kitchen."*

**Most likely to fail live:** a dense A4 letter is the *long-input* case, which is exactly
where the measured 4.74 tok/s hurts most — and the board filling slowly is worse than it
filling wrong. Second risk: the judge pattern-matches it to "document summariser" (an
explicit anti-pattern in `docs/08` §5.7) before the wifi-off beat lands.

**Fallback:** the golden path runs on eight pre-tested letters with cached JSON behind
`DEMO_OFFLINE` — the judge still picks which one, so the choice stays live. Force
short structured output (four fields, no prose). And the recorded fallback **must open
on the router being unplugged** — if the video starts at the upload button, the whole
point is gone.

---

## 3. Second Look — wow 4

`xmodel-fable.md`, idea 1. **Track 1 (Most Creative Hack with Gemini 3.7 Flash).**

The best pure Amit-Vadi-keynote demo in the corpus. The agent step timeline is the
device that makes agentic tool use *visible* — which is the single highest-leverage
presentation trick available today, and the thing that separates this from a chat
window. The judge supplies a listing nobody could have staged.

**Opening sentence:** "Open any secondhand listing on your phone — I'll tell you what
it's actually worth and what's wrong with that exact model."

**The 90 seconds:**

| Time | Beat |
|---|---|
| 0:00–0:08 | Opening sentence. Judge opens Vinted / eBay / Marketplace on their own phone. |
| 0:08–0:16 | They screenshot it into the app. |
| 0:16–0:46 | The agent timeline runs, visibly, one row at a time, each ticking green with its own result: `identifying → Ercol dining chair, ~1970s` · `searching sold comps → 11 results` · `searching known faults → seat joint glue failure`. **Do not narrate this. Let them watch it.** |
| 0:46–1:06 | Verdict card: "Asking £140. Recent sold range £70–95. Check the seat joints — this model's glue fails. Ask the seller these three questions." |
| 1:06–1:20 | Judge checks the comps against their own phone. That verification beat is worth more than anything you can say. |
| 1:20–1:30 | The number. |

**The quotable number:** *"15 minutes of nervous googling before you message a seller →
30 seconds, and it caught £45 of overpricing on a listing I'd never seen."*

**Most likely to fail live:** venue wifi plus a 3–4 call grounded chain is the worst
latency profile of any top-5 idea, and free tier is ~15 RPM — a queue of judges each
firing a chain will throttle. A stalled timeline reads as broken.

**Fallback:** hard-cap the live chain at **two** calls; pre-cache fault sheets for five
common categories (bike, sofa, console, phone, chair) so step three is instant; keep
the timeline animating during any wait so latency reads as work rather than a hang. On
a 429, degrade to the cached category checklist — degraded but never blank. Recorded
45-second run on a real listing, shot by 16:30.

---

## 4. Get Me A Human — wow 4

`inbox-comms.md`, idea 2. **Track 1.** The most demo-*safe* idea in the top five:
text in, diagram out, no camera, no microphone, no props, no on-device dependency.

Two things earn its score. The judge invents the input from nothing — no props to
pre-stage means nothing to fake. And the payoff is a **drawn diagram**, not prose,
which is the fastest way to dodge the "this is a chatbot answer" reflex.

**Opening sentence:** "Make up the most annoying phone menu you've ever had to sit
through — say it out loud, and I'll map you the way out."

**The 90 seconds:**

| Time | Beat |
|---|---|
| 0:00–0:08 | Opening sentence. |
| 0:08–0:26 | Judge invents it: "Press 1 for billing, 2 for technical, to speak to someone press 9, then hold, then press 9 again…" Presenter types it as they speak. |
| 0:26–0:42 | The decision tree draws itself node by node. |
| 0:42–0:56 | The loop the judge invented flashes red: **"dead end — returns you to the main menu."** They put that trap in themselves, so they know it wasn't planted. |
| 0:56–1:12 | The fastest path to a human highlights end to end: `1 → 4 → 0`. |
| 1:12–1:30 | The number. |

**The quotable number:** *"An unknown 12-option phone menu → the exact four button
presses to a human, mapped in 15 seconds."*

**Most likely to fail live:** the source file names it — live-mic mode depends on
`starter/06_live_voice_agent.py`, whose own docstring flags the send-audio path as
**UNVERIFIED**. Attempting it on stage is the single riskiest 20 minutes in that whole
file. Second, softer risk: the judge invents a menu with no circular trap, so the red
flash never fires and the demo is one grade flatter.

**Fallback:** **cut live-mic entirely.** Text-paste is the golden path; the presenter
types while the judge talks, which looks like transcription anyway and cannot fail.
Prompt the model to flag *either* a loop *or* a hold-time trap *or* a
buried-human-option, so something always lights red. Recorded run on a real bank IVR
transcript.

---

## 5. Which Button — wow 4

`xmodel-fable.md`, idea 4. **Track 2.**

The most unfakeable input in the corpus. The team does not choose the machine, does not
choose the goal, and has never seen the panel. If it works, no judge can suspect a
rehearsal. It is also the one demo you perform by walking the judge somewhere, which
breaks the table-side format in a way people remember.

**Opening sentence:** "Pick any machine in this building — I've never seen its control
panel, and neither has the model."

**The 90 seconds:**

| Time | Beat |
|---|---|
| 0:00–0:10 | Walk to the venue's coffee machine. Airplane mode already on and visible. |
| 0:10–0:20 | Judge states any goal: "make it stronger", "smaller cup", "descale it". |
| 0:20–0:38 | Camera frame → panel comes back with every button labelled. |
| 0:38–0:56 | Three steps, spoken aloud by the device. |
| 0:56–1:16 | **The judge presses the buttons. Coffee happens.** That is the payoff — a physical outcome, not a screen. |
| 1:16–1:30 | "There is no wifi in a launderette basement. That's the point." Then the number. |

**The quotable number:** *"Ten minutes hunting a manual nobody kept → ten seconds, on a
machine we'd never seen, with the network off."*

**Most likely to fail live:** a confidently hallucinated button label, in front of the
one judge who owns that exact machine. Then: glare on a reflective panel wrecking the
overlay alignment; then the measured on-device speed missing the "ten seconds" claim.

**Fallback:** drop live AR overlay for a **captured still with numbered circles** — the
source file is right that this loses nothing in the pitch and removes the hardest
engineering risk. Use confidence phrasing in the output itself ("likely the eco toggle —
short press to test"), which converts a wrong answer into an honest one. Keep cloud
Gemini wired as a silent quality path for the days the offline claim isn't the pitch.
Record the fallback on the venue's actual machine at 16:30 once the room thins out.

---

# The gaps — where score and substance disagree

**This is the most useful thing in this document. Read it before picking.**

## Three of my top five rest on the same unproven bet

Overshare Check, Doormat and Which Button all require **Gemma 4 multimodal running
locally and fast**. Nothing in this repo proves that works. `docs/05` says
`gemma4:e4b` is natively multimodal, so the *capability* is real — but
`starter/07_local_gemma.py` is text-only over Ollama, the `images=[...]` param is
undemonstrated anywhere, MediaPipe LLM Inference with Gemma 4 multimodal in-browser over
WebGPU is a bigger unknown again, and the only number anyone has measured on this
hardware is 4.74 tok/s with a 65-second cold load. The risk is **call shape and speed**,
not whether the model can see.

The asymmetry matters: `travel-commute.md` (updated since I first read it) now records a
confirmed Gemini-side shape —
`client.interactions.create(model="gemini-3.7-flash", input=[image, prompt], response_format={schema})`
— so the *cloud* image path is architecturally settled and only needs 20 minutes of
plumbing. The *local* image path is settled nowhere. That is precisely why the cloud-safe
tier below is the honest hedge.

**Spend the first 20 minutes proving one working local image call before building
anything on top of it.** If that spike fails, the entire top of this ranking collapses
and you fall back to the cloud-safe tier: **Second Look** and **Get Me A Human**, both
of which are Track 1, both of which only need a Gemini image or text call, and neither
of which can be killed by a slow laptop.

## Strong idea, weak demo

- **Blind-Spot Wayfinder** (`travel-commute.md` 1) — conceptually the best on-device
  argument in the corpus: offline isn't a feature, it's the premise, because platform
  tunnels have no signal. But the demo asks a small local model to do spatial reasoning
  on a photographed, angled, glare-covered station map — the hardest visual task here —
  and its own premise forbids a cloud fallback. Great pitch, fragile 90 seconds.
- **Decision Archaeologist** (`work-learning.md` 2) — genuinely uses the 1M-token context
  window, the same technique that won the last comparable GDM hackathon. But "I read all
  of it in one pass" is invisible. A judge sees a summary and files it under meeting
  summariser in eight seconds.
- **Packet Cross-Exam** (`xmodel-gpt.md` 3) — the evidence-thread UI (a line drawn from
  the front-of-pack claim to the exact back-label figure that supports or contradicts it)
  is the best "make the reasoning visible" device anyone proposed. It is attached to a
  problem no judge is feeling in that room, and can dead-end on "not computable".
  **Steal the evidence-thread UI for whatever you build.**
- **CareThread / CheckLine** (`care-relationships.md` 1, 2) — real problems, real users,
  and CheckLine has the cleanest prior-art gap in its file. Both demos need seeded weeks
  of history the judge cannot verify, and both stall visibly on measured on-device speed.
- **Is This Real?** (`inbox-comms.md` 1) — scored 4 and nearly made the top five. Held
  out because the category is saturated to the point of collision: **Gemma Guard was
  built for an actual Gemma hackathon** doing screenshot → on-device Gemma → scam verdict,
  privacy angle included. A GDM judge may well know it. That's a caveat before the payoff.

## Weak idea, strong demo

- **Watchword** (`xmodel-gpt.md` 4) — the best twenty seconds in the whole corpus. The
  judge invents the trigger ("ring when the red cup moves behind the blue one"), performs
  it with their own hands, and the payoff is a binary event: it rings or it doesn't.
  Nothing to read, nothing to interpret, impossible to fake. And the product underneath
  is a phone alarm. **It is also the least buildable idea here** — a 1 fps local VLM
  loop on a laptop measured at 4.74 tok/s cannot catch a short transition. Do not build
  it. Do steal the shape: *let the judge define the success condition, then let them
  trigger it themselves.*
- **Bottle Cam** (`health-body.md` 1) — near-perfect judge-supplied moment (their own
  object, instant answer, verifiable with their own eyes) attached to the thinnest product
  in the corpus. Scores nothing beyond "Gemini reads an image" against a rubric that
  weights Model Leverage at 30% and Innovation at 25%. A great party trick that loses on
  the scorecard.
- **Backseat Games** (`xmodel-fable.md` 6) — the pocket-dump is delightful and
  unrehearsable, and the judge keeps the game. But it generates *prose rules*, which is
  precisely the long-generation case the measured doc says is not stage-viable on this
  hardware, and a 30%-technical rubric will file it under "toy".
- **Bin Whisperer** (`home-food.md` 4) — "the judge hands you literal rubbish" is a
  top-five physical moment attached to a feature a UK council already shipped.
- **Carry-On Security Checker** (`travel-commute.md` 5) — the pocket-dump demos
  beautifully; the idea fails its own frequency filter (people fly a few times a year).

## One structural warning

**Big Font** (`xmodel-fable.md` 5) scored 3 rather than 4 for a purely practical reason
that no one in the source file caught: its wow is *handing the judge a printed A4 sheet*,
and there is unlikely to be a printer at Imperial. Without the print, it is a nicely
typeset page on a screen — a whole grade lower. If you pick it, confirm a printer exists
before 14:00, or re-stage the payoff as something physical you can actually produce.

## Track allocation, if you want the arbitrage

Three separate £400 prizes means picking the track where you are strongest *relative to
who else enters it*. Expect Track 1 (Gemini 3.7 Flash) to be the most crowded — it's the
default. Track 2 (Gemma, local only) will have the fewest entries and the most failures,
because on-device is genuinely hard and most teams will discover the speed problem at
16:00. If your local spike succeeds by 13:30, Track 2 is the softest field. If it fails,
Track 1 with **Second Look** is the safe strong play.
