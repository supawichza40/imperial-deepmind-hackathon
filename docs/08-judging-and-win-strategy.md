# Judging & Win Strategy: UK AI Agent Lab, Gemini Edition (22 Aug 2026)

This event's own rubric, tracks, and judge panel get announced at the 12:30 briefing, and nothing online matches this exact title or date. Everything below comes from published rubrics and outcomes of the closest comparable events: Google DeepMind's own Gemini 3 Hackathon (Feb 2026, $100K in prizes, the most recent and most directly comparable event, same sponsor and same year), Google Cloud's ADK Hackathon, the Gemini Live Agent Challenge, the 2024 Gemini API Developer Competition, and Kaggle's Gemma 3n Impact Challenge. Claims about a past event are sourced inline. Recommendations for today are marked **JUDGEMENT**.

---

## If you read nothing else

Judges score technical execution highest (25-50% across every published rubric), but in a 2-3 minute live look they can only *perceive* your demo and your one-sentence pitch, not read your code. So the real game is: build the smallest thing that makes a judge feel the "wow" in 90 seconds, using a feature Google just shipped (Gemini 3.7 Flash's agentic tool use or Gemma 4's on-device multimodal), narrate it like a person who understands their own tech, and have a recorded backup in case your live call hits a rate limit.

Four numbers to hold in your head:
- **Idea locked by 13:00.** Everything after that is execution, not exploration.
- **One feature, not three.** Every judging source that discusses losers says the same thing: half-finished feature lists lose to one polished workflow.
- **Submit by 17:00, not 17:30.** The last 30 minutes belong to platform hiccups, not building.
- **Public link, no login.** A demo judges can't open scores as if it doesn't exist.

---

## 1. What published rubrics actually weigh

| Event | Technical execution | Innovation/wow | Impact | Presentation/demo | Source |
|---|---|---|---|---|---|
| Gemini 3 Hackathon (GDM, Feb 2026) | 40% | 30% | 20% | 10% | [gemini3.devpost.com/rules](https://gemini3.devpost.com/rules) |
| ADK Hackathon (Google Cloud) | 50% | 30% | n/a | 20% (demo + docs) | [googlecloudmultiagents.devpost.com](https://googlecloudmultiagents.devpost.com/rules) |
| AI Builders Hackathon (Google AI) | 25% | 20% | 25% | 15% (+15% UX/design) | [ai-builders-hackathon-2026.devpost.com](https://ai-builders-hackathon-2026.devpost.com/) |
| Code with Gemini API | unweighted: creativity, technical execution, Gemini use, impact, presentation | | | | [code-api.devpost.com](https://code-api.devpost.com/) |

The pattern holds across all four: technical execution is always the single biggest bucket (25-50%), innovation is always second (20-30%), and presentation/demo is almost always the smallest formal weight (10-20%), despite being the only category judges directly experience in a live round. Devpost's own generic guide adds two categories most Google-specific rubrics fold into the above: ease of use ("if you can't explain how to use your project in a sentence or two, it might be too complicated") and design ([info.devpost.com](https://info.devpost.com/blog/understanding-hackathon-submission-and-judging-criteria)).

**JUDGEMENT:** expect this event's rubric to land in the same range. Technical execution as the plurality weight, an explicit "did you use Gemini/Gemma meaningfully" line item, and demo/presentation formally small but practically decisive, because it's the only category judges score from direct observation rather than a written description.

## 2. What actually won comparable events

Gemini 3 Hackathon (Feb 2026, GDM, $100K pool), the closest analog to today:
- **Grand Prize: Globot**, a 5-agent supply-chain crisis system. Named agents (*Market Sentinel*, *Risk Hedger*, *Logistics Orchestrator*, *Compliance Manager*) each own one job; the Compliance Manager reads 500-page insurance policies using Gemini's 2M-token context window. Pitch line: turns "sudden supply chain chaos into confident decisions in 60 seconds." ([devpost.com/software/globot-341w9q](https://devpost.com/software/globot-341w9q))
- **2nd: Aegis, Autonomous Multi-Agent Crisis Command**
- **3rd: Netra, Empowering the Visually Impaired**
- Honorable mentions: AgentGuard (a "semantic firewall for the agentic web"), BatteryForgeAI, Logic Lift, PROCSee, Proofy.AI, Agent-weaver, Orbital.
([gemini3.devpost.com/forum_topics/43515](https://gemini3.devpost.com/forum_topics/43515-winners-announced))

ADK Hackathon (Google Cloud, 2025, $50K, 10,400+ participants):
- **Grand Prize: SalesShortcut**, a multi-agent SDR system (lead gen, research, proposal, outreach), praised for "exceptional skill, ingenuity, and a deep understanding of ADK."
- Regional winners: **Energy Agent AI** (energy customer management), **Edu.AI** (autonomous essay grading and study plans, Brazil), **GreenOps** (cloud sustainability audit agent), **Nexora-AI** (personalized education, EMEA).
- Honorable mentions: Particle Physics Agent (natural language to validated Feynman diagrams), TradeSageAI, Bleach (visual agent builder).
([cloud.google.com/blog: ADK hackathon results](https://cloud.google.com/blog/products/ai-machine-learning/adk-hackathon-results-winners-and-highlights))

Gemini Live Agent Challenge: every winner in it was voice-first and hands-free.
- **Grand Prize: ORION**, a voice-directed surgical co-pilot that lets a surgeon get real-time answers and visual assistance without breaking scrub.
- **drone-copilot**: natural voice control of a drone instead of a joystick or menus.
- **Sankofa**: voice turns family histories into narrated, illustrated stories.
- **Moonwalk and Wand**: voice-plus-gesture, hands-free desktop and browser control.
- **JohnKeats.AI**: a voice-only emotional companion reading pitch, pacing, and tone.
- **Rayan Memory**: a voice-built, explorable 3D "memory palace."
([cloud.google.com/blog: Gemini Live Agent Challenge](https://cloud.google.com/blog/topics/developers-practitioners/winners-and-highlights-of-the-gemini-live-agent-challenge))

Gemini API Developer Competition (2024): Vite Vere (visual guidance for cognitive disabilities), Outdraw (a draw-to-fool-the-AI game), Prospera (a real-time AI sales coach), Jayu (a multimodal, OS-level assistant), ViddyScribe (video audio-description for blind users). ([developers.googleblog.com](https://developers.googleblog.com/en/announcing-the-winners-of-the-gemini-api-developer-competition/))

Kaggle Gemma 3n Impact Challenge (600+ submissions, 8 winners, on-device theme): Vite Vere's Gemma 3n rebuild ran the same cognitive-disability assistant fully offline; a separate winner fine-tuned Gemma 3n to translate pictograms into a specific nonverbal user's own voice; the AI Edge special prize went to an app built on MediaPipe's LLM Inference API with streamed on-device responses. ([kaggle.com/.../hackathon-winners](https://www.kaggle.com/competitions/google-gemma-3n-hackathon/hackathon-winners), [blog.google](https://blog.google/innovation-and-ai/technology/developers-tools/developers-changing-lives-with-gemma-3n/))

Patterns across all five events (**JUDGEMENT**, drawn from the above):
1. Winners are named, narrow workflows, never platforms. "A supply-chain crisis reasoning engine" or "a surgical voice co-pilot," never "an AI tool for businesses."
2. Multi-agent entries name each agent's job (Market Sentinel, Risk Hedger, and so on). That's a presentation device as much as an architecture choice: it lets a judge grasp "orchestration" in one sentence.
3. Accessibility and offline/on-device framing wins disproportionately with Google judges specifically. Vite Vere won twice, once in the cloud track and once on-device.
4. Winners build around whatever the sponsor just shipped. Every Live Agent Challenge winner used real-time interruption and turn-taking, the feature that challenge existed to showcase; Globot's standout technical detail was the 2M-token context window, Gemini 3's newest headline number at the time. Judges recognize and reward visible use of the thing they just launched.
5. Voice and hands-free interaction is the single most repeated new interaction paradigm that wins. It's the easiest way to make a demo look like agentic AI rather than a chatbot wearing a new skin.

## 3. The scoring reality of a 5-hour hackathon with a live demo

A judge spends roughly 90 seconds to 3 minutes per project live, per the JetBrains judge-table writeup and Devpost's own "5 judges" post, both of which describe judges physically clicking through and using the product rather than reading about it ([blog.jetbrains.com](https://blog.jetbrains.com/ai/2026/06/how-to-win-a-hackathon-notes-from-the-judging-table/), [info.devpost.com/blog/hackathon-judging-tips](https://info.devpost.com/blog/hackathon-judging-tips)). A forum investigation into the Gemini 3 Hackathon's own third-place result found that even though Technical Execution was formally weighted 40%, judges were not required to actually run the code, so the submission's written description carried more real weight than anyone assumed ([gemini3.devpost.com forum thread](https://gemini3.devpost.com/forum_topics/43667-third-place-was-a-prompt-injection-attack-devpost-and-google-owe-participants-an-answer)).

**What this means (JUDGEMENT):** what judges can perceive in the room (a working click-path, a one-sentence problem statement, a specific model feature named out loud, a presenter who sounds like they built it) outweighs anything invisible: your test coverage, your clean service boundaries, your commit history, how close you came to not finishing. Since a subset of teams do a live demo round today, that risk cuts both ways: a live click-path can also fail in front of judges in a way a recorded video cannot. Spend your 4 working hours on what a judge will actually see and hear in under 3 minutes, not on correctness nobody will check.

## 4. Idea-selection heuristics and candidate ideas

Heuristics (**JUDGEMENT**, derived from section 2):
- Prefer a new interaction paradigm (voice, hands-free, autonomous multi-step) over a better chat window.
- Name your agents' jobs out loud in the pitch. It's the cheapest way to make "multi-agent orchestration" legible in 10 seconds.
- Bias toward whichever keynote feature you can demonstrate unambiguously on screen: Gemini 3.7 Flash's agentic tool-calling and multi-step planning (launched 13 Aug 2026, "our most intelligent workhorse model yet for coding and agents," [appwrite.io](https://appwrite.io/blog/post/gemini-37-flash), [datanorth.ai](https://datanorth.ai/news/google-releases-gemini-3-7-flash)) or Gemma 4's on-device multimodal capability (edge-tier E2B/E4B, native function-calling, runs with no network, [blog.google](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemma-4-12b/), [ai.google.dev model card](https://ai.google.dev/gemma/docs/core/model_card_4)).
- Offline/on-device demos have a structural demo-safety advantage: they can't hit a rate limit or lose wifi on stage.

| # | Idea | Wow moment | Gemini/Gemma feature shown | Build risk | Why a GDM judge cares |
|---|---|---|---|---|---|
| 1 | **Crisis command copilot**: named agents (monitor, risk, router) watch a live feed and converge on one recommendation | Judges watch 3 agents visibly hand off and agree in real time | Gemini 3.7 Flash multi-step tool-calling and planning | Medium: needs a believable, live-ish data source | Near-identical shape to the last GDM hackathon's own Grand Prize and 2nd place |
| 2 | **Hands-busy voice co-pilot**: talks someone through a physical task (cooking, first aid, repair) via webcam while their hands stay busy | Presenter's hands never touch a keyboard; agent corrects a live mistake | Gemini Live API real-time voice and vision | Medium: needs a reliable, low-latency audio/video pipe | Mirrors every single Live Agent Challenge winner's interaction paradigm |
| 3 | **Fully offline accessibility companion**: image or pictogram input turns into spoken guidance, with zero network use | Pull the wifi cable and it still works | Gemma 4 on-device (E2B/E4B), native function-calling | Low to medium: on-device inference setup takes real time to get right | Directly demonstrates the other keynote feature; matches Vite Vere, the only project to win two separate Google/Gemma competitions |
| 4 | **Prompt-injection firewall for agents**: detects and blocks an attack against another agent, live | A judge suggests an attack phrase and it gets caught on screen | Gemini 3.7 Flash as both attacker-simulator and detector | Medium: must be an honest, narrow detector, not a gimmick | Directly on-theme for agent safety; a real controversy just happened over exactly this failure mode at GDM's own hackathon (see section 5) |
| 5 | **Live browser task agent**: Gemini's computer-use tool drives a real browser through a multi-step task a judge calls out | "You ask, it clicks": narrated live automation | Gemini computer-use tool | High: UI automation is the flakiest category here | Computer use is a fresh, actively promoted capability judges will recognize |
| 6 | **Research, critique, and report pipeline**: three agents (researcher, critic, writer) produce a cited answer to a live question in under a minute | Speed, plus visible disagreement between agents before consensus | Gemini 3.7 Flash long-context and tool use, ADK-style orchestration | Low to medium | Directly mirrors the ADK Grand Prize's orchestration narrative |
| 7 | **Meeting or lecture co-pilot, hybrid cloud and edge**: the Live API captures the room while Gemma 4 on-device produces a private local summary afterward | "It kept listening after we left the room, and it never left this laptop" | Both keynote features in one demo | Medium to high: two integration surfaces to get working | Puts both keynotes on display without picking one |
| 8 | **Point-and-diagnose offline**: point a camera at a broken appliance, plant, or car part and get an instant offline fix | Works in airplane mode | Gemma 4 multimodal, on-device | Low to medium | Same "impossible before now, works with no wifi" wow as #3 |
| 9 | **Long-document compliance agent**: drop in a huge policy or contract and get instant, cited answers | Feed it something absurdly long and get an answer in seconds | Gemini's 2M-token context window | Low | Same technique Globot's Compliance Manager used to win Grand Prize |
| 10 | **Underserved-language on-device tutor**: offline translation and teaching for a language poorly served by big models | A language most demo audiences have never seen an AI handle well | Gemma 4 multilingual, on-device | Medium | Strong fit for the Potential Impact category; mirrors Google's own "Unlock Global Communication with Gemma" framing |
| 11 | **Voice and gesture accessibility navigator**: hands-free computer control for users with motor impairments | A full desktop task completed with voice and a wave, no mouse | Gemini Live API plus computer use, combined | High: the hardest combination on this list | Combines two flagship capabilities; a direct analog to Moonwalk and Wand, both category winners |
| 12 | **Agent-vs-agent negotiation**: two agents representing opposite sides negotiate a deal live while judges set the terms | A genuinely unscripted-feeling back-and-forth | Gemini 3.7 Flash agentic reasoning, tool-calling into a shared ledger | Low to medium | Visibly agentic rather than a chat wrapper; fun, memorable, and easy to narrate |

**JUDGEMENT: the safest picks for a 4-working-hour build, in order.** #9 first (lowest risk, still shows a real Gemini strength), then #6 or #3 (medium risk, strong narrative fit), then #1 or #2 if the team already has comfortable tooling for live data feeds or audio/video. Avoid #5 and #11 unless someone on the team has already made browser/UI automation reliable before today. That combination is the single riskiest category researched.

## 5. Anti-patterns: what loses

1. **Chatbot wrapper with no meaningful model integration.** Judges are explicitly looking for AI doing something genuinely novel, not just parsing a form ([lablab.ai](https://lablab.ai/guide/how-to-win-an-ai-hackathon)).
2. **No public, login-free demo.** The Gemini 3 Hackathon's own rules require a link that "should be publicly accessible and not require a login" ([gemini3.devpost.com/rules](https://gemini3.devpost.com/rules)); a working local demo that judges can't open scores as if it were broken ([momen.app](https://momen.app/blogs/hackathon-backend-that-doesnt-break-demo-day)).
3. **Live API calls that fail on stage.** Rate-limit failures during live demos are a documented, recurring hackathon problem ([dev.to](https://dev.to/azaynul10/building-a-voice-controlled-web-agent-for-the-gemini-hackathon-and-how-i-beat-the-api-rate-limits-13m4)). Mock or cache the call your demo depends on, and always have a recorded fallback.
4. **Too much scope.** "Multiple half-finished features lose to one polished workflow. Scope creep guarantees failure" ([blog.jetbrains.com](https://blog.jetbrains.com/ai/2026/06/how-to-win-a-hackathon-notes-from-the-judging-table/)).
5. **Missing baseline eligibility requirements.** "You'd be surprised how many submissions are disqualified simply because they didn't meet the baseline criteria" ([info.devpost.com](https://info.devpost.com/blog/understanding-hackathon-submission-and-judging-criteria)). Read this event's rules the moment they're published at 12:30, before writing a line of code.
6. **Backend with no visible UI, or the reverse (a mockup with nothing running behind it).** One judge specifically warns against submissions "extremely back-end heavy" with minimal UI; another explicitly checks whether a team actually coded and deployed something that works, versus just designing a prototype.
7. **A templated idea that looks like everyone else's.** "Projects that stand out the most are the ones that depart the most from that template," in a Google judge's own words ([info.devpost.com/blog/hackathon-judging-tips](https://info.devpost.com/blog/hackathon-judging-tips)).
8. **Gaming the rubric in the write-up itself.** At the Gemini 3 Hackathon, the community accused the third-place project of writing its submission text as direct instructions to an LLM judge (opening "A Note to the Judges," section headers mapped one-to-one onto the published 40/30/20/10 rubric, closing with "the clear and obvious choice for the Grand Prize"). Devpost was still investigating it as of the last public update ([forum thread](https://gemini3.devpost.com/forum_topics/43667-third-place-was-a-prompt-injection-attack-devpost-and-google-owe-participants-an-answer)). The legitimate lesson is different from the manipulative one. Structure your honest write-up around the published criteria so a judge can map your project to their scorecard in seconds, but never write anything addressed to the judge as an instruction, and don't assume nobody will actually run your code, because sometimes they do.
9. **Ignoring the sponsor's tech.** Every published rubric here has an explicit "did you use Gemini/ADK meaningfully" line. A generic build that could have used any LLM under the hood loses that whole category by default.

## 6. Time budget: 12:30 to 17:30 (4 working hours net, 1-hour lunch)

| Time | Block | Checkpoint |
|---|---|---|
| 12:30-13:00 | Briefing, tracks announced, read the rules in full, pick an idea from section 4 matched to whatever track is announced | **Idea locked by 13:00** |
| 13:00-13:30 | Repo scaffold, API keys wired and one test call succeeds, roles split, seed data decided | Environment proven working before lunch |
| 13:30-14:30 | **Lunch.** Talk architecture over food; don't block progress on anyone finishing here | n/a |
| 14:30-15:15 | Build the full path end to end, however ugly, so input to output works at least once. Grab a GDM mentor now if stuck; office hours just opened and the queue is shortest | **End-to-end skeleton by 15:15** |
| 15:15-16:00 | Build the *one* wow feature from section 4 to a polished state. Stub or mock everything off that golden path | One feature, fully working |
| 16:00-16:30 | **Feature freeze.** Bug fixes and error-state handling only. Rehearse the pitch once, out loud | **Feature freeze by 16:30** |
| 16:30-16:50 | Record the fallback demo video using the exact rehearsed script and seed data | **Demo recorded by 16:50** |
| 16:50-17:00 | Write the roughly 200-word submission text, attach video, public link, and repo, then submit | **Submitted by 17:00** |
| 17:00-17:30 | Buffer for platform issues, final pitch rehearsal, be ready if called for a live demo round | Slack time, not build time |

**JUDGEMENT:** never target 17:30 as your actual submit time. Every account of Devpost-style submissions mentions last-minute upload congestion. Treat 17:00 as the deadline and 17:30 as a dead zone you should already be clear of.

## 7. Demo-day tactics

2-minute script structure (**JUDGEMENT**, built from the JetBrains and Devpost judge advice above):
1. Hook (10 seconds): one sentence that makes the judge feel the frustration you're solving, not a feature list.
2. Insight (15 seconds): why this wasn't buildable before now, naming the specific Gemini or Gemma feature that unlocks it.
3. Live demo (90 seconds): walk the judge through it as a user would experience it, narrating confidently, and say the model or feature name out loud at least once.
4. Impact and close (15 seconds): one concrete before-and-after number, then one sentence on what's next.
5. Leave about 10 seconds of slack for an immediate question.

**Recording the fallback:** record it at the 16:30-16:50 checkpoint using the exact rehearsed script and the same seed data as the live version, so switching to it mid-pitch if a live call fails looks deliberate, not panicked.

**Seed data:** pre-load one deterministic, impressive example. Never type live input during your 2 minutes; you should already be past the point of waiting on a keystroke.

**What's on screen:** the golden-path UI only. Close everything else (no dev console, no Slack, one browser tab) unless the terminal output is the point, for example when judges are watching agents hand off to each other.

**The one number to quote:** something the judge can repeat to the next judge without looking at notes, a concrete before-and-after claim such as "cut a 45-minute task to 60 seconds," the same shape Globot used in its own pitch.

## 8. Judge-question objection bank

1. "What happens if that API call fails right now?" Show that you already handled it: mention the retry or fallback path, and that this is exactly why you rehearsed with a recorded backup.
2. "How is this different from wrapping ChatGPT or another LLM?" Name the specific Gemini or Gemma capability (a tool-calling loop, 2M-token context, on-device inference, Live API turn-taking) that a plain wrapper couldn't do.
3. "Did you really build this in a few hours?" Be upfront about any starter template or boilerplate used. Judges expect it: one judge's own advice is to use "familiar tools... starter repos," not to hide it.
4. "What's the business model, and who actually uses this?" One sentence naming the user and why they'd want it. Don't inflate the market size.
5. "Can I try it myself?" Have the public, login-free link ready before they ask. If the event format doesn't support that, hand over the laptop.
6. "What breaks if I use it in a way you didn't expect?" Name your two or three known failure modes before they find them. Honesty about limits reads as confidence, not weakness.
7. "Why does this need an agent instead of a simple script?" Point to the specific decision or multi-step judgment call the agent makes that a fixed script structurally can't.
8. "What would you build next with another week?" Have one credible, scoped next step ready. It signals product thinking without undercutting what you already shipped.

---

*Sources are inline throughout. Anything about today's specific event (rubric, tracks, judge panel) was unpublished at the time of writing and should be checked against the 12:30 briefing before locking an idea.*
