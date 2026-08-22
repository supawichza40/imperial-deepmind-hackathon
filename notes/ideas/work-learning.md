# Work & Learning — candidate ideas

Domain: work and learning, ordinary adults, non-obvious angles only. Excludes anything
already covered in `docs/08-judging-and-win-strategy.md` §4 (crisis command copilot,
hands-busy voice co-pilot, offline accessibility companion, prompt-injection firewall,
browser task agent, research/critique/writer pipeline, meeting/lecture hybrid co-pilot,
point-and-diagnose offline, long-document compliance agent, underserved-language tutor,
voice/gesture navigator, agent-vs-agent negotiation) and the banned templates in §8
brief (meeting summariser, resume tailor, chat-with-your-documents, generic RAG,
flashcards, note-taking app).

Two candidates started this pass and were killed before reaching this list: a live
Socratic exam-revision examiner (killed — Socra, hisocra.com, already ships this almost
exactly) and a camera-based homework helper coaching the parent instead of solving the
problem (killed — "Homework Helper — Tutor" on the App Store already ships this exact
positioning). A physical-skill-mirroring coach (compare your form to a reference video,
live, frame by frame) was dropped on feasibility, not prior art — it needs either real
pose-estimation CV not in the starter kit, or per-frame Gemini calls that blow the 15 RPM
budget in under a minute; not reducible to a 3-hour build.

---

```
IDEA 1 — Spot the Gap
Problem in one sentence: I sent someone instructions and they did the wrong thing, because what was obvious to me wasn't obvious to them.
Who and how often:            Anyone who delegates or briefs another person — a manager assigning a task, a parent texting a babysitter, someone emailing a contractor or a colleague covering for them. Misread instructions causing redone work is one of the most common weekly frictions in ordinary work.
The 90-second wow:            Judge pastes a real instruction they've actually sent someone — an email, a Slack message, a text to a contractor, live, their own words. The agent doesn't fix grammar — it simulates being the recipient executing the instructions step by step and surfaces the 2-3 exact points where it would have to guess (which version, by when, whose sign-off), each with the one clarifying question that resolves it.
Google feature named out loud: Gemini 3.7 Flash's agentic multi-step reasoning (thinking_level: high, per docs/03) — this needs genuinely stepping through the instructions as an executor would, not a single classification pass.
Closest existing thing:       Grammarly, Professionally.ai (professionally.ai), Rephrasely email checkers (rephrasely.com/checkers/email) — Delta: those score tone and grammar. None of them execute the instructions as a reader would and report where the plan breaks down task-mechanically (who, which version, by when). No shipped product doing task-simulation ambiguity detection for everyday delegation surfaced in this search pass.
Build in 3h:                  app.py (Flask) + templates/index.html (one textarea, paste-in) + prompts.py (04_structured_output.py-style schema: ambiguities[] with {phrase, why_ambiguous, clarifying_question}). Riskiest 20 min: tuning the prompt so it finds real task-mechanical gaps instead of grammar nits — needs several passes on genuinely messy real text before it reliably reads like task simulation rather than a spellchecker.
When the API throttles:       One call per submission, trivially under 15 RPM. If wifi dies, fall back to local Gemma 4 (07_local_gemma.py, per docs/05) — pure text in/out with no real-time requirement, so the measured 4.74 tok/s / 65s cold load is tolerable for a single demo pass, unlike anything needing back-and-forth turns.
Quotable number:              Turns an instruction that would have bounced back and forth over email three times into one that lands right the first time.
Which track it fits:          productivity / agents
Kill risk:                    If the model just paraphrases the instructions back instead of genuinely finding task-mechanical gaps, it reads as generic writing feedback and the wow evaporates — must be tested on real messy input before the demo, never on a written-in-advance example.
```

```
IDEA 2 — Decision Archaeologist
Problem in one sentence: I joined this project three weeks after everyone else decided how it works, and nobody has time to walk me through the whole history.
Who and how often:            Anyone new to a team, project, or committee — a new hire, someone back from leave, a volunteer joining a running project. "Why do we do it this way" comes up most weeks in any fast-moving team.
The 90-second wow:            Judge pastes a real, messy chain of text — a Slack thread export, an email chain, a run of doc comments, live from their own inbox if they have one open. The agent reconstructs in one pass: what was decided, who disagreed and why, and what's still explicitly unresolved — distinguishing settled from still-open.
Google feature named out loud: Gemini 3.7 Flash's 1,048,576-token context window (docs/03) — the same technique the last comparable GDM hackathon's Grand Prize winner (Globot) used to read 500-page insurance policies in one pass (docs/08 §2); here a whole quarter's decision history goes in as one prompt with nothing chunked or dropped.
Closest existing thing:       Slack AI's thread recap (slack.com/help/articles/25076892548883) and software-scoped ADR-generation tools like adr-agent (github.com/macromania/adr-agent) — Delta: Slack AI needs live Slack OAuth access (a hard filter violation here) and doesn't reconstruct dissent; ADR agents are scoped to software-architecture decisions specifically. This is zero-integration paste-anything, and it explicitly surfaces disagreement and open questions rather than just recapping what was said.
Build in 3h:                  app.py + templates/index.html (textarea) + prompts.py (04-style schema: decision, rationale, dissent[], open_questions[]). Safest build of the five per feasibility review — pure text in, structured text out, no camera or audio pipeline at all.
When the API throttles:       One call per paste, trivial load. Fully viable on local Gemma 4 as an offline fallback since it's pure text reasoning with no real-time requirement — the safest fallback of any idea in this set.
Quotable number:              Turns three weeks of "wait, why do we do it that way" side conversations into one two-minute read.
Which track it fits:          productivity / agents
Kill risk:                    The most crowded category researched — "summarize this thread" tooling is everywhere. If the demo doesn't visibly put the dissent and open-questions fields on screen, a judge files it under the banned "meeting summariser" anti-pattern on sight.
```

```
IDEA 3 — Rubber-Duck Handover
Problem in one sentence: I know exactly what I was doing on this yesterday, and I will have completely forgotten by Monday.
Who and how often:            Anyone context-switching between tasks or projects — most people multiple times a week, and acutely every Friday afternoon and Monday morning.
The 90-second wow:            Judge talks for 60-90 seconds about anything they're mid-way through, live, off the cuff. The agent asks 2-3 sharp follow-up questions live that clearly react to what was just said ("what's blocking you on that?", "who's waiting on you?"), not canned prompts, then produces a structured brief. The judge then asks a days-from-now-style question ("why did I do it that way?") and gets the answer pulled straight from the brief.
Google feature named out loud: Gemini 3.7 Flash's agentic multi-turn tool use — deciding what information is missing and asking for it live is the actual agentic behavior on display, not transcription.
Closest existing thing:       Standuply's voice/video standup capture (range.co/compare/geekbot) and AI voice-journaling apps like BrainFlow (braindumpnotes.app) — Delta: those post the raw recording or run generic reflective journaling. Neither runs a live, targeted interview aimed at closing the specific gaps a work handover needs, and neither is built for later retrieval by asking "why did I do X."
Build in 3h:                  app.py + templates/index.html (MediaRecorder for mic capture, textarea fallback built in from the start) + prompts.py + a small JSON store for briefs. Riskiest 20 min: getting browser mic capture into a format the API reliably accepts — test this first, before any prompt logic.
When the API throttles:       Text-paste fallback uses the identical call path, not a separate code path bolted on later. ~4 calls per session, well under 15 RPM.
Quotable number:              Cuts the 10 minutes of Monday-morning "wait, where was I" down to a 30-second read.
Which track it fits:          agents / productivity
Kill risk:                    The delta is real but narrow — if the demo doesn't visibly show a follow-up question reacting to what the judge just said, it reads as a voice-journaling app with extra steps.
```

```
IDEA 4 — Jargon Cartographer
Problem in one sentence: Everyone in this meeting just said three acronyms in one sentence and I'm too new to ask what any of them mean.
Who and how often:            Anyone in their first weeks at a new job, team, or industry — daily during onboarding, tapering to multiple times a week for months afterward.
The 90-second wow:            Judge photographs or pastes a real jargon-heavy message — an internal doc excerpt, a Slack message thick with acronyms. Instead of a flat glossary, the agent builds a live interactive map showing how the unfamiliar terms relate to each other and to the surrounding context — for example, revealing that two acronyms name the same underlying system under two different teams' labels.
Google feature named out loud: Gemini 3.7 Flash's multimodal input (image + text in one call, per docs/03) plus structured JSON output driving a client-side relationship graph, not a text answer.
Closest existing thing:       Google's own NotebookLM Mind Maps (9to5google.com/2025/03/27/notebooklm-mind-map) — paste or upload a document, Gemini generates an interactive branching concept map. Delta: NotebookLM maps topic structure within one uploaded document; this is scoped specifically to unfamiliar terms, pulls in context beyond the one pasted snippet, and accepts a photo of a physical or half-legible message as input. Real delta, but this is the single riskiest prior-art collision in the set — the comparison product is Google's own, at a Google event.
Build in 3h:                  app.py + templates/index.html (hand-rolled canvas/SVG force-graph, no CDN dependency given unreliable wifi) + prompts.py (nodes/edges schema). Riskiest 20 min: rendering an interactive graph client-side with zero external libraries — genuinely harder than the model call itself.
When the API throttles:       One call per document. Keep one static example doc with a precomputed graph JSON as an offline fallback, following the starter kit's own demo_fallback.md pattern, so a dead connection doesn't kill the whole demo.
Quotable number:              Turns a five-minute "wait, what does that even stand for" Slack derail into a ten-second glance.
Which track it fits:          on-device / productivity / accessibility
Kill risk:                    A GDM judge sees the interactive map and says "isn't this just NotebookLM" before the delta is stated out loud — the pitch must open with the delta, not let the judge discover the resemblance first.
```

```
IDEA 5 — Did I Get That Right?
Problem in one sentence: My manager just explained something to me once, out loud, and I need to know if what I heard is actually what they meant before I go and do it.
Who and how often:            Anyone getting verbal instructions or a walkthrough from a colleague, manager, or client — common in the first months at a job, and a recurring risk anywhere instructions are given once, verbally, with no written record.
The 90-second wow:            Judge (or a second person) gives a short, specific explanation out loud; the judge then paraphrases it back in their own words. The agent doesn't grade against general knowledge of the topic — it diffs the paraphrase against that specific original explanation and flags exactly where it drifted, in order of what matters most.
Google feature named out loud: Gemini 3.7 Flash's audio input plus long-context comparison across two spoken passages in a single call.
Closest existing thing:       Socra, a shipped Socratic AI tutor for exam revision (hisocra.com), and ReExplain (producthunt.com/products/reexplain), which has you explain a concept to the AI so it can find gaps against its own knowledge. Delta: both compare your explanation to the AI's general knowledge of a subject. This compares your paraphrase to one specific real explanation someone just gave you, catching the case where a colleague's version was non-standard or company-specific and the textbook answer would actively mislead you.
Build in 3h:                  app.py + templates/index.html (two capture slots: original, paraphrase) + prompts.py (04-style schema: matches[], drifted[], missed[]). Same shape as idea 3 but lower build risk — no live follow-up-question loop, just two inputs and one comparison call.
When the API throttles:       Both inputs can be typed instead of spoken; one call total, trivial load.
Quotable number:              Catches the misunderstood instruction before it becomes the wrong piece of work, not after.
Which track it fits:          productivity / accessibility
Kill risk:                    The most crowded space researched — two close shipped comparisons exist (Socra, ReExplain), and the delta (one specific transcript, not general knowledge) is the kind of distinction a judge can miss in 90 seconds unless the two-input structure is visually obvious the instant the demo opens.
```

---

## Ranking (best first)

1. **Spot the Gap** — cleanest prior-art delta of the five, safest build (single text call, no camera/audio), and it needs genuine agentic multi-step reasoning rather than classification, so it clears the "did you use Gemini meaningfully" bar without a stretch.
2. **Decision Archaeologist** — safest build overall and the one idea that shows a genuinely distinguishing Gemini strength (the 1M-token context window) using the exact technique the last comparable hackathon's Grand Prize winner used — held back only by needing the dissent/open-questions fields kept visible on screen so it doesn't read as a generic summarizer.
3. **Rubber-Duck Handover** — the best live "judge supplies the input" moment of the five and the clearest agentic multi-turn demo, held back only by a real but narrow delta from voice-journaling apps.
4. **Jargon Cartographer** — highest visual wow factor but the single riskiest prior-art collision in the set, since the closest comparable product is Google's own NotebookLM Mind Maps, live at a Google event.
5. **Did I Get That Right?** — weakest of the five; two close shipped comparisons exist (Socra, ReExplain) and the delta is subtle enough that a rushed 90-second demo could easily read as "another Socratic tutor."
