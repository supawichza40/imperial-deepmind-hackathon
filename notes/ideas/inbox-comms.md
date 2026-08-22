# Inbox and comms — 5 candidate ideas

Domain: email, WhatsApp/iMessage, phone calls, voicemail, scheduling with humans, saying no,
spam/scam messages, customer service phone trees, language barriers, the awkward message
you've been avoiding. No third-party OAuth anywhere — every idea below takes paste-in, file
upload, camera, or microphone as input only.

Started with 6 candidates. Killed 2 on prior art before writing them up:
- **"Say That Again"** (cross-generational/cultural text decoder — literal meaning + subtext +
  suggested reply) — killed. Near-total overlap with shipped apps SubText AI, "Decoded: True
  Intent AI," and ReadMind, all doing paste-text → tone/intent/reply today. Also collapses into
  the auto-reject "AI assistant for X" pattern.
- **"Rehearsal Room"** (mic-based roleplay rehearsal for an awkward conversation, ending in a
  drafted message) — killed. Functionally the same product as shipped apps Text Simulator,
  Tough Tongue AI, and Harco, which state this exact purpose almost verbatim.

The 5 below survived prior art and got a feasibility pass against the actual starter kit
(`starter/01-08_*.py`, `docs/03-gemini-3.7-flash.md`, `docs/05-gemma-4-on-device.md`) and the
measured on-device numbers in `notes/MEASURED-on-device-reality.md` (Gemma 4 via Ollama:
~4.74 tok/s, ~65s cold load — fine for short structured JSON output, not for long generation).

---

```
IDEA 1 — Is This Real?
Problem in one sentence (a person's words, not a market description):
    "I just got a text saying my bank account's locked, click here to fix it — is this a scam or not?"
Who and how often:            Most UK/US adults now receive multiple scam/phishing texts and
                               emails per week (bank-fraud alerts, delivery-fee scams, HMRC/DVLA
                               impersonation, "your package is on hold") — this is one of the
                               highest-frequency annoyances in the whole domain, hitting nearly
                               every phone-owning adult multiple times weekly.
The 90-second wow:            Judge pastes a real scam text/email they've actually received (or
                               a sample if they don't have one handy) into the box. In seconds:
                               a verdict (SCAM / LEGIT / UNSURE), the exact phrases that gave it
                               away highlighted, and one recommended action (block/report/ignore).
                               Toggle "private mode" and it re-runs entirely on-device via local
                               Gemma 4 — no network call at all, judge can watch the wifi icon.
Google feature named out loud: Gemma 4 on-device (LiteRT/Ollama local inference) for the private
                               path — screenshots and texts often contain account numbers and
                               bank details, so running the scan without sending them anywhere is
                               the actual point, not a gimmick. Gemini 3.7 Flash structured output
                               for the cloud path (verdict + red flags + action as one typed call).
Closest existing thing:       Fishy: Phishing & Scam Guard (https://apps.apple.com/us/app/fishy-phishing-scam-guard/id6504583500),
                               ScamScan (https://apps.apple.com/us/app/scamscan-ai-scam-detector/id6760021038),
                               ScanSheild AI, Devpost (https://devpost.com/software/scansheild-ai)
                               — Delta: every one of these sends the message to a cloud LLM API
                               with, at best, a privacy disclaimer. None run locally. If this
                               genuinely runs on-device for the private path, that's a real,
                               defensible difference — the delta lives or dies on actually
                               shipping local inference, not claiming it.
Build in 3h:                  is_this_real.py (structured output per 04_structured_output.py's
                               pattern — Pydantic Verdict{verdict, red_flags[], action, why});
                               sample_data/scam_samples/ (2-3 pre-made texts + screenshots,
                               never live-capture, per demo_fallback.md); gemma_local.py cloning
                               07_local_gemma.py's Ollama client for the private toggle. Riskiest
                               20 minutes: screenshot mode needs a multimodal image-input request
                               — docs/05 confirms gemma4:e4b is natively multimodal (a real
                               vision encoder, `ollama run gemma4:e4b`), but no script in this
                               kit shows the actual image-call shape for either the cloud or
                               local path, so it's architecturally sound but unverified until
                               tested live. Text-paste is the safe, proven golden path.
When the API throttles:       Real, but narrower than "everything works offline." Per
                               notes/MEASURED-on-device-reality.md's own guidance (measured on
                               this exact machine: 4.74 tok/s, 65s cold load, most tokens burned
                               on visible chain-of-thought), the local path is only demo-viable
                               if the model is pre-warmed before the judge walks up, thinking
                               tokens are suppressed, and the on-device schema is trimmed — drop
                               the free-text "why" field from the local path specifically and
                               keep it cloud-only; a full verdict+flags+action+why response as
                               prose is exactly what the measured doc calls not stage-viable.
                               Text mode keeps working with the wifi cable pulled; screenshot
                               mode has no offline path at all.
Quotable number:              A 3am panic-read of a bank-fraud text → a verdict and the exact
                               three words that gave it away, in under 10 seconds.
Which track it fits:          safety / on-device
Kill risk:                    If "private mode" turns out to just be an API call with a privacy
                               disclaimer rather than real local inference, this collapses into a
                               duplicate of Fishy/ScamScan with zero delta — a judge who asks "is
                               that actually running locally?" and gets a dodge kills it on the
                               spot. Local inference for the private path is not optional polish
                               here, it's the entire idea.
```

```
IDEA 2 — Get Me A Human
Problem in one sentence (a person's words, not a market description):
    "Press 1 for this, press 2 for that — I just want to talk to an actual person and I don't know which button gets me there."
Who and how often:            Roughly weekly for anyone mid-way through any piece of life admin
                               (insurance claim, delivery dispute, GP referral, bank query,
                               subscription cancellation) and several times a month baseline for
                               most adults — the honest claim is "at least weekly during any
                               active admin task," not every single week year-round.
The 90-second wow:            Judge makes up an annoying fake IVR menu on the spot and reads it
                               out loud, or types it in ("Press 1 for billing, press 2 for
                               technical, to speak to someone press 9 then hold for 20 minutes
                               then press 9 again..."). In seconds, a decision-tree diagram
                               appears showing the fastest path to a human, with any deliberately
                               circular "dark pattern" loops flagged in red.
Google feature named out loud: Gemini 3.7 Flash agentic multi-step reasoning/tool use — parsing
                               an arbitrary, never-seen-before menu structure into a graph is a
                               genuine multi-step reasoning task, not a lookup.
Closest existing thing:       GetHuman (https://apps.apple.com/us/app/gethuman/id306141756),
                               DoNotPay "Skip Waiting On Hold" (https://techcrunch.com/2019/10/16/avoid-waiting-on-hold/)
                               — Delta: both rely on a crowdsourced database of known companies'
                               shortcuts, or a callback bot that waits on hold for you. Neither
                               parses the actual live or uploaded IVR audio/script in real time —
                               so neither works on a menu that isn't already in someone's
                               database. This candidate works on any menu, live, with no database.
Build in 3h:                  ivr_decoder.py (04_structured_output.py's pattern — Pydantic
                               DecisionTree{nodes, edges, dark_patterns[]}) plus a small
                               tree-render helper (~20 lines, not in the starter kit);
                               audio_upload.py for an uploaded audio-clip mode. Riskiest 20
                               minutes: a true live-mic mode needs 06_live_voice_agent.py's
                               real-time audio streaming — but that file's own docstring flags
                               the actual send-audio path as "UNVERIFIED... not fetched from
                               Gemini docs." Attempting live-mic mode live is the single riskiest
                               20 minutes across all 5 ideas in this file.
When the API throttles:       Text-paste mode falls back to local Gemma cleanly (short JSON tree
                               output is the stage-viable case). Audio-clip and live-mic modes
                               have no local fallback at all — no ASR shipped in the kit, and
                               Ollama's gemma4 audio-in path is unconfirmed — so those modes just
                               break offline. Scope: text-paste is the must-work golden path.
                               Two independent feasibility passes against this exact starter kit
                               agree live-mic mode (06_live_voice_agent.py's real audio streaming)
                               cannot be built to a working state inside a 3-hour budget — treat
                               it as out of scope, not a stretch goal to attempt and fall back
                               from. Uploaded-audio-clip mode is the only multimodal stretch worth
                               attempting, and only after text-paste is solid.
Quotable number:              An unknown 12-option phone menu → the exact 4 button-presses to a
                               human, mapped in 15 seconds.
Which track it fits:          agents / productivity
Kill risk:                    Attempting live-mic mode at all — portaudio install issues, mic
                               permission prompts, and an untested streaming-audio call, live, on
                               stage, is exactly the kind of 20 minutes that eats the whole
                               budget and leaves nothing to show. Scope it out before building,
                               not after running out of time.
```

```
IDEA 3 — Voicemail Triage
Problem in one sentence (a person's words, not a market description):
    "Someone left me a 45-second voicemail I can barely make out — do I need to call them back, and if so what do I even say?"
Who and how often:            Several times a week for most adults once robocalls, delivery
                               drivers, doctor's-office callbacks, and unknown-number spam are
                               counted alongside genuine voicemails — spam/robocall volume alone
                               puts most phone owners into multiple unwanted voicemails a week.
The 90-second wow:            Judge records a short voicemail live via the mic (reading a script
                               like "this is Dr. Smith's office, please call back to confirm your
                               appointment") or uploads a sample audio file. Output: transcript,
                               a legit-vs-scam read, the one action needed, and a ready callback
                               script with the exact phrases to say — and exactly what not to
                               agree to over the phone (never confirm personal details unprompted).
Google feature named out loud: Gemini 3.7 Flash audio understanding (transcribe + reason over the
                               same input) via the Interactions API's audio modality.
Closest existing thing:       YouMail and RingCentral AI Transcription (https://www.ringcentral.com/ai-transcription.html)
                               — transcript + spam/scam flag on voicemails, already shipped;
                               Google Pixel Call Screening does live on-device scam detection.
                               Delta: transcript + risk-label is commodity, all three already do
                               it. A generated, ready-to-use callback script plus an explicit
                               "what not to agree to" layer was not found in any shipped consumer
                               voicemail app — those all stop at transcript + label.
Build in 3h:                  voicemail_triage.py (audio upload → interactions.create with audio
                               input → structured Pydantic {transcript, assessment, action_item,
                               callback_script}); record_voicemail.py (record-once-then-upload via
                               pyaudio+wave — simpler and safer than real-time streaming).
                               Riskiest 20 minutes: the audio-input request shape appears nowhere
                               in any of the 8 starter scripts, so the first real call either
                               works in 5 minutes or burns an hour with no way to know in advance
                               — and combining audio input with a structured-output response in
                               one call (needed for the transcript+assessment+action+script
                               schema) is a pairing this kit never demonstrates, so budget for a
                               two-call fallback (transcribe, then extract) if the combined call
                               doesn't behave.
When the API throttles:       Weak — the least safe fallback of the five ideas here. Gemma 4 has
                               a native audio encoder on paper, but Ollama's exposed API for
                               gemma4 audio input is unconfirmed; even if it works, transcribing
                               then reasoning to a full callback script at the measured 4.74 tok/s
                               (287 tokens ≈ 2m9s for a two-sentence answer) blows past
                               demo-viable. If wifi or quota dies mid-demo, this one breaks —
                               pre-record a golden-path transcript+response backup per
                               demo_fallback.md and be ready to read from it.
Quotable number:              A confusing 45-second voicemail → the one thing to do and the exact
                               words to say back, in 10 seconds.
Which track it fits:          productivity / accessibility (also helps anyone with phone anxiety
                               or hearing difficulty who avoids calling back at all)
Kill risk:                    No genuine offline fallback. If wifi drops or the 15 RPM limit hits
                               mid-demo and there's no pre-recorded backup ready, the golden path
                               dies on stage with nothing to show — this is the idea most likely
                               to need the recorded-fallback safety net, not just have one.
```

```
IDEA 4 — Group Chat Unstick
Problem in one sentence (a person's words, not a market description):
    "There's 47 unread messages in the group chat about Saturday and I still don't know what the actual plan is or if I'm supposed to reply."
Who and how often:            Multiple times a week for anyone in more than two or three active
                               group chats (family plans, friend trips, flat/house logistics,
                               a work or society WhatsApp) — the chaotic multi-person planning
                               thread is one of the most common everyday text-based frustrations.
The 90-second wow:            Judge pastes their own real group chat scrollback (or a provided
                               sample of 15 people arguing about a dinner reservation). Output in
                               seconds: the currently decided plan (if any), the names of people
                               who still haven't responded, and one ready-to-send nudge/poll
                               message to actually unstick the thread.
Google feature named out loud: Gemini 3.7 Flash structured output over messy, informal,
                               long-context text — extracting decision-state (not notes) from
                               real chaotic chat requires the same long-context handling the
                               keynote demoed.
Closest existing thing:       GistGem, Chrome extension (https://chromewebstore.google.com/detail/gistgem-whatsapp-group-ch/pdeglbcbdehfjfllclngapefcppbbjmp),
                               ThreadRecap (https://www.threadrecap.com/en/blog/summarize-whatsapp-chat-using-ai)
                               — Delta: both extract decisions/action items from a WhatsApp
                               scrollback, which is the core mechanism here too — this is the
                               thinnest delta of the five. What neither does: explicit
                               "who hasn't responded yet" tracking, or auto-generating a
                               ready-to-send nudge/poll message. Screenshot-only ingestion (no
                               WhatsApp Web export needed) for a 10+-person thread is also
                               thinner ground than either competitor covers.
Build in 3h:                  chat_unstick.py — near-identical to 04_structured_output.py's
                               pattern (Pydantic Plan{decided_plan, non_responders[],
                               nudge_message}); screenshot mode reuses the same unverified
                               image-input path as Idea 1. Riskiest 20 minutes isn't
                               infrastructure — it's prompt reliability: real scrollback has
                               nicknames, no timestamps, and reactions instead of replies, which
                               makes "who hasn't responded" genuinely ambiguous. Budget time to
                               test against 3-4 real sample chats, not just one clean example.
When the API throttles:       The best fallback of the five, with one caveat. Output is short —
                               a plan, a name list, one message — which is the case the
                               measured-reality doc calls stage-viable for gemma4:latest, but
                               only pre-warmed with thinking suppressed; keep the non-responder
                               list and nudge message genuinely short (a handful of names, one
                               line), not full prose, to stay inside a demo-safe response time.
                               With that discipline it's a genuine, working local path.
Quotable number:              47 unread messages in a group chat → the actual decided plan and
                               who still needs a nudge, in 15 seconds.
Which track it fits:          productivity
Kill risk:                    This is the one most exposed to the brief's explicit auto-reject
                               list — "paste chat → LLM summary" is structurally close to
                               "another meeting summariser," just retargeted at group texts. It
                               only survives if the responder-tracking and the generated
                               nudge message are the headline of the demo, not the summary — if
                               the pitch leads with "it summarizes your chat," a judge will
                               pattern-match it to the reject list in the first ten seconds.
```

```
IDEA 5 — Actually, When?
Problem in one sentence (a person's words, not a market description):
    "We've been going back and forth for twelve messages about when to meet up and I honestly can't tell what times actually work for everyone anymore."
Who and how often:            Several times a week for anyone who coordinates plans by text —
                               friends, family, a service provider (plumber, tutor, dog walker),
                               a small team without shared calendars — a lower-confidence claim
                               than the scam-text or spam-voicemail frequency cases above, but
                               real for most socially active adults.
The 90-second wow:            Judge pastes a messy real (or provided sample) back-and-forth text
                               thread — "Tuesday's bad for me," "can't do mornings," "I'm free
                               after 6 except Thursday" — from three or more people. Output in
                               seconds: each person's stated constraints laid out clearly, three
                               concrete proposed times that satisfy all of them, and one
                               ready-to-send message.
Google feature named out loud: Gemini 3.7 Flash structured output for constraint extraction and
                               satisfaction over free-text natural language, with no calendar API
                               involved at all — the reasoning has to solve a real small CSP from
                               prose, not just extract a date.
Closest existing thing:       When2meet and WhenIsGood (classic group-scheduling poll tools),
                               and AI calendar assistants like Reclaim.ai (https://reclaim.ai) —
                               Delta: When2meet/WhenIsGood require every participant to
                               separately fill in a new availability grid; Reclaim.ai and similar
                               AI schedulers require a connected calendar account (the exact
                               OAuth flow this brief bans). Nothing found parses an *existing*,
                               already-messy text thread directly into proposed times with zero
                               account connection and zero new form for anyone to fill in.
Build in 3h:                  untangle_schedule.py — same safe pattern as Idea 4
                               (04_structured_output.py's Pydantic ScheduleProposal{
                               constraints_per_person[], proposed_times[3], ready_message}).
                               Riskiest 20 minutes: prompt reliability on genuinely contradictory
                               or ambiguous real threads ("can't do Tues," "Wed's also bad for
                               me," no year given for a date) — same class of risk as Idea 4, plus
                               needing to feed today's actual date into the prompt so "next
                               Tuesday" resolves correctly.
When the API throttles:       Same safe short-output profile as Idea 4 — a genuine, working local
                               Gemma fallback (structured, short JSON output, stage-viable per the
                               measured-reality numbers).
Quotable number:              12 messages of "does Tuesday work?" back-and-forth → 3 times that
                               actually work for everyone, in 15 seconds.
Which track it fits:          productivity
Kill risk:                    Least dramatic wow of the five — "here are 3 times" doesn't have
                               the emotional payoff of a scam verdict or a solved phone-menu
                               maze, so on a 90-second judge walk-by this is the one most likely
                               to read as a minor feature rather than a standout product unless
                               the presenter explicitly narrates the constraint-solving happening
                               live.
```

---

## Ranking, best first

1. **Is This Real?** — Highest frequency of any idea here (multiple scam texts/week is now
   near-universal), the strongest "judge supplies input live" wow, and it plays directly to Ian
   Ballantyne's own keynote framing (privacy-first offline workflows) — but the entire delta
   collapses to zero if local inference isn't real. Build the on-device path first, not last.
2. **Get Me A Human** — The cleanest prior-art delta of the five (a genuine mechanism gap, not a
   repositioning) and a strong visual wow (a decision tree materializing from an unknown menu).
   Scope hard to text-paste only; live-mic is the single riskiest 20 minutes in this whole file
   and should be cut the moment the build falls behind.
3. **Voicemail Triage** — A real, specific delta (the callback script + "don't agree to" layer)
   that no shipped competitor has, but the weakest safety net of the five: no confirmed offline
   fallback and an untested audio-input call shape. Only take this if a pre-recorded backup is
   genuinely ready before the pitch, not as an afterthought.
4. **Group Chat Unstick** — The safest possible build (best local fallback, most proven API
   pattern) but the thinnest prior-art delta and the one closest to an explicit auto-reject
   pattern. Worth building only if the pitch leads with responder-tracking and the nudge message,
   never with "it summarizes your chat."
5. **Actually, When?** — Solid, safe, genuinely differentiated from OAuth-requiring calendar
   tools, but the least dramatic 90-second wow of the five and the softest frequency claim. A
   reasonable fallback pick if the team wants the lowest-risk build, not the strongest pitch.
