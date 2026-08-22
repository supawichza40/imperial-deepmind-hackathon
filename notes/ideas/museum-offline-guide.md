# Offline Museum Guide — art interpretation with no signal

**Track 2 or 3.** Status: candidate as of 13:35, 22 Aug 2026.

## One line
Point a phone at any artwork inside a museum with no signal and get a spoken
interpretation, because the model is on the device.

## The problem
Museum wifi and mobile signal are famously bad — thick walls, basements, crowds. Audio
guides cover a curated handful of works, cost money, and say the same thing to everyone.
Anything not on the official route gets no explanation at all. Visitors stand in front of
a piece with no idea what they are looking at, holding a device that could tell them if
only it had a connection.

Not limited to paintings: sculpture, installations, textiles, architecture, artefacts,
street art.

## How it works

**Offline, on device (Gemma 4 multimodal):**
- Camera captures the artwork.
- Gemma describes what is physically present: composition, subject, materials, technique,
  colour, condition, style period.
- Answers follow-up questions about what the visitor can see in front of them.
- Works in airplane mode. This is the demo moment.

**Online, when signal exists (Gemini 3.7 Flash):**
- Identifies the specific work and artist via Google Search grounding.
- Adds provenance, historical context, the artist's other work, critical reception.
- Cross-references what the visitor saw earlier in the visit.

The visitor never sees a failure. The experience degrades to "rich description of what is
in front of you" rather than "no connection".

## Why it scores

| Criterion | Weight | Why this fits |
|---|---|---|
| Technical Execution & Model Leverage | 30% | On-device multimodal inference is the hard part and the visible one. Graceful cloud upgrade when grounding is available. |
| Innovation & Originality | 25% | Inverts the audio guide: no curation, no pre-recording, works on anything in the room. |
| Real-World Impact & UX | 25% | Strong accessibility case for blind and low-vision visitors, who are badly served by visual-only displays. Also education and tourism. Matches the organisers' named "offline education & civic utilities" and "assistive & accessibility agents" prompts. |
| Presentation & Live Demo | 20% | **Airplane mode is the pitch.** Turn the wifi off on stage and it still works — the one demo that cannot fail from a dead network. |

## The two-minute demo

1. Hold up a printed artwork (or point at one in the room). Show the phone/laptop is in
   airplane mode.
2. Capture it. Gemma describes composition, technique, mood — spoken aloud.
3. Ask a follow-up: *"what's happening in the background?"* Still offline.
4. Turn wifi on. Gemini identifies the actual work, adds who painted it, when, and why
   it matters.
5. Show the same flow on a sculpture or a textile to prove it is not painting-specific.

## Build notes and risks

- **The demo hardware question decides this idea.** True phone deployment needs LiteRT /
  MediaPipe and Android work — that is not a 4-hour job from scratch. A laptop webcam
  version with the network visibly disabled makes the same point and is achievable.
  Decide this in the first 15 minutes, not at 16:00.
- **Do not host local inference on the lead's M1** — 10.8 tok/s and it slows the machine.
  Run the offline half on whichever teammate's machine is fastest.
- **Descriptions must stay short** at that token rate. Two or three sentences spoken, with
  "tell me more" as a follow-up, beats a paragraph the audience waits through.
- **Accessibility framing needs care, not decoration.** If the pitch claims blind and
  low-vision users, the output should be structured the way description guidelines
  actually recommend — overall impression first, then detail, and never "as you can see".
- **Be honest about identification.** Offline Gemma describes; it does not reliably know
  *which* specific painting it is. Claiming otherwise is the kind of thing a judge will
  test live. The honest split — offline describes, online identifies — is also the
  stronger architecture story.

## Scope for 4 hours

1. Webcam or uploaded image in, spoken description out, network off.
2. One follow-up question turn.
3. Wifi-on path: Gemini with Search grounding names the work and adds context.
4. A visible network-state indicator so the audience always knows which model answered.

Cut first: phone deployment, museum-specific databases, multi-work session memory.

## Versus Privacy Gate

Both are Track 3-shaped and both make the local model load-bearing. Privacy Gate has the
stronger enterprise and impact story; this has the more theatrical demo and a cleaner
one-sentence pitch. This one is also more exposed to the "can you really run it on a
phone" question — see the hardware note above.
