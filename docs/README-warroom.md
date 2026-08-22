# UK AI Agent Lab: Gemini Edition — war room

Google DeepMind × UK AI Agent Lab · London · **Saturday 22 August 2026**
Build window **12:30 → 17:30** (hard deadline). Winners announced by Mon 24 Aug.

Everything in this repo exists to save minutes during those five hours.

## Read in this order

| # | File | What it's for | When |
|---|---|---|---|
| 00 | [docs/00-ground-truth.md](docs/00-ground-truth.md) | Organiser's own words: schedule, speakers, prizes. The authority. | Now |
| **10** | **[docs/10-tracks-rules-rubric.md](docs/10-tracks-rules-rubric.md)** | **ANNOUNCED: 3 tracks, rubric weights, 4 required submission artefacts. Authoritative.** | **Now** |
| 01 | [docs/01-event-brief.md](docs/01-event-brief.md) | Event/organiser recon, tracks, rules, prior editions | Now |
| 02 | [docs/02-speakers-and-mentors.md](docs/02-speakers-and-mentors.md) | Who to talk to, what to ask, mentor-hour protocol | Before 11:05 |
| 08 | [docs/08-judging-and-win-strategy.md](docs/08-judging-and-win-strategy.md) | Rubric, what wins, 15 sized ideas, minute-by-minute plan | **12:15–12:30** |
| 07 | [docs/07-setup-keys-quotas-cost.md](docs/07-setup-keys-quotas-cost.md) | Key, SDK, quotas, 429 survival | 12:30 |
| 03 | [docs/03-gemini-3.7-flash.md](docs/03-gemini-3.7-flash.md) | Model IDs, limits, pricing, what's new | 12:30 |
| 04 | [docs/04-gemini-agent-api.md](docs/04-gemini-agent-api.md) | Tool use, grounding, Live API, structured output — with code | While building |
| 05 | [docs/05-gemma-4-on-device.md](docs/05-gemma-4-on-device.md) | Gemma 4 local: Ollama/MLX/LiteRT, M1 reality check, fine-tune | While building |
| 06 | [docs/06-agent-frameworks-adk-a2a-mcp.md](docs/06-agent-frameworks-adk-a2a-mcp.md) | ADK, A2A, MCP, Gemini CLI — pick a stack | 12:30 |
| — | [starter/](starter/) | `git clone` → working agent in 10 min | 12:30 |
| 09 | [docs/09-submission-and-demo.md](docs/09-submission-and-demo.md) | Submission templates, video, run-sheet, panic protocol | **15:00 onward** |

## Rubric (announced) — 100 points

Technical Execution & Model Leverage **30%** · Innovation & Originality **25%** ·
Real-World Impact & UX **25%** · Presentation & Live Demo **20%**

Three tracks, each with an identical prize (£400 + US$300 credits + swag): Track 1
Gemini 3.7 Flash · Track 2 Gemma 4 local · Track 3 hybrid. Track choice is a
competitive decision — see [docs/10](docs/10-tracks-rules-rubric.md).

**Required by 17:30:** public GitHub repo (README, setup, architecture diagram,
MIT/Apache licence) · proof of model integration · 2-min Loom/YouTube video ·
2–3 paragraph write-up.

## The two pillars (from the keynotes)

1. **Gemini 3.7 Flash** — frontier agent behaviour in the cloud. Amit Vadi, 11:05.
2. **Gemma 4 on-device** — LiteRT, offline, private, specialised medical/multimodal weights. Ian Ballantyne, 11:20.

A project that uses both — cloud brain plus a local private path — is aimed at this room.

## Hard checkpoints

| Time | Must be true |
|---|---|
| 12:30 | Tracks known, idea locked, roles assigned |
| 13:00 | Repo up, keys working, hello-world call succeeded |
| 14:00 | End-to-end skeleton runs — ugly but complete |
| 15:00 | **Draft submission created** (empty is fine — claim the slot) |
| 16:00 | Feature freeze. Polish only after this. |
| 16:45 | Demo video recorded. Mentors gone at 16:45. |
| 17:10 | **Submitted.** 20 minutes of buffer, not zero. |
| 17:30 | Deadline. Nothing lands after this. |

## Rules of the day

- Submit a draft at 15:00. A late submission scores zero regardless of the code.
- Never put a live API call on the critical path of the demo without a cached fallback.
- Record the fallback video before you need it.
- Talk to a DeepMind mentor before 15:30, not at 16:40.

## Provenance

`docs/00` is organiser-supplied ground truth. Every other doc was researched live on
22 Aug 2026 by parallel agents and carries inline source URLs; unverifiable claims are
marked `UNVERIFIED`. Trust 00 over everything else.
