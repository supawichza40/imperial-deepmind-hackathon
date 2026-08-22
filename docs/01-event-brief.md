# Event Brief — UK AI Agent Lab: Gemini Edition (22 Aug 2026, Imperial College London)

Prepared for a participant hacking **today**. Ground-truth facts from the organisers are marked accordingly; everything else is sourced or explicitly flagged as unverified/inference.

---

## 1. CONFIRMED schedule (organiser ground truth) + countdown to deadline

| Time (BST) | Block | Countdown to 17:30 deadline |
|---|---|---|
| 10:30 | Doors open | T-7:00 |
| 10:30–11:00 | Registration / networking | T-6:30 |
| 11:00 | Intros | T-6:30 |
| 11:05–11:20 | Keynote — Amit Vadi (GDM), "Frontier Agents with Gemini 3.7 Flash" | T-6:10 |
| 11:20–11:40 | Keynote — Ian Ballantyne (GDM), "On Device AI with Gemma 4" | T-5:50 |
| 11:40–11:55 | Q&A — Denish KC, AI GTM Lead @ Google | T-5:35 |
| 11:55–12:15 | Break | T-5:15 |
| 12:15–12:30 | Hackathon briefing, sign-up, **TRACK ANNOUNCEMENT** | T-5:00 |
| **12:30** | **Hacking begins** | **T-5:00** |
| 13:30–14:30 | Lunch | T-3:00 |
| 14:30–16:45 | Hacking + GDM mentor office hours | T-0:45 at 16:45 |
| **17:30** | **HARD SUBMISSION DEADLINE** | **T-0:00** |
| 17:30–18:00 | Networking | — |
| 18:00 | Space closes | — |

**Net build time: 5 hours (12:30–17:30), with a 1-hour lunch inside it → ~4 hours of real coding time.** Budget accordingly: the track isn't known until 12:15, so nothing track-specific can be pre-built — but tooling, boilerplate, and Gemini/Gemma API setup can be done before 12:30 (see §7).

An earlier organiser draft also mentioned a panel and a "top 3–5 projects demo" round; this did not appear in the confirmed schedule above, so treat a live demo round as **possible but unconfirmed** — prepare a tight demo just in case.

---

## 2. Event identity (researched)

- **Full name:** UK AI Agent Lab: Gemini Edition
- **Date confirmed via registration page:** Saturday 22 August [2026]
- **Venue:** Imperial College London — City and Guilds Building, Exhibition Rd, South Kensington, London SW7 2AZ ([aiagentslab.uk/events](https://www.aiagentslab.uk/events), [Luma listing](https://luma.com/7srz7k7v))
- **Organisers (co-hosts):** UK AI Agents Lab, Imperial FinTech & Blockchain (Imperial College Union society), Google DeepMind ([aiagentslab.uk/events](https://www.aiagentslab.uk/events), [Luma listing](https://luma.com/7srz7k7v))
- **Registration:** via Luma — https://luma.com/7srz7k7v (host-approval required; page showed only a handful of spots left)
- **Community:** UK AI Agents Lab's own Discord — https://discord.gg/h7Jk9DfV8W; Twitter/X https://x.com/iclblockchain; LinkedIn https://www.linkedin.com/company/imperial-blockchain; contact hello@aiagentslab.uk ([aiagentslab.uk](https://www.aiagentslab.uk/))
- A **WhatsApp group** was also referenced on the event's own Luma page, but no invite link could be captured — get it at check-in.

### Who runs UK AI Agents Lab
Public pages don't name individual founders. It's built as a multi-university effort ("An ecosystem for builders shaping what comes next"), with 12 partner universities including Imperial, Cambridge, Oxford, UCL, KCL, LSE, TUM, EPFL, KU Leuven ([aiagentslab.uk](https://www.aiagentslab.uk/)). Past hackathon listings name **Imperial AI Society** and **Imperial Blockchain & FinTech Society** as the on-the-ground co-hosts at Imperial ([search result summary of EP5 Luma/somo.social listing](https://luma.com/knoymap5)).

Lab-wide stated stats (self-reported, unverified against independent sources): 500+ builders, 50+ projects, £250K+ prizes across the programme ([aiagentslab.uk](https://www.aiagentslab.uk/)); a separate stats block elsewhere on the site claims "2,000+ builders / 15+ universities / $200K+ cumulative prizes / 200+ projects" — the two figures don't fully reconcile, so treat both as self-reported marketing numbers, not audited facts.

### Speakers (researched, cross-checked against LinkedIn snippets in search results — not independently opened/verified on LinkedIn itself)
- **Amit Vadi** — Head of Community, Google DeepMind Developer Experience (DevX), based in London. Prior Kaggle competition host (e.g. "Vibe Code with Gemini 3 Pro in AI Studio") ([Kaggle](https://www.kaggle.com/amitvadi), [LinkedIn snippet via search](https://uk.linkedin.com/in/amitvadi), [X](https://x.com/vadiamit)).
- **Ian Ballantyne** — Developer Relations Engineer at Google DeepMind (9 years in Google DevRel), works on Gemini/Gemma, focuses on on-device AI via Google AI Edge; has publicly demoed Gemma running multi-agent workloads on Pixel/Raspberry Pi/Jetson hardware ([GDG event page](https://gdg.community.dev/events/details/google-gdg-on-campus-imperial-college-london-london-united-kingdom-presents-ai-horizons-a-conversation-with-ian-ballantyne-from-google-deepmind/), [LinkedIn snippet via search](https://uk.linkedin.com/in/ianballantyne)).
- **Denish KC** — listed on LinkedIn as AI GTM Lead, Google Cloud AI (ex-Revolut) ([LinkedIn snippet via search](https://uk.linkedin.com/in/denishkc)).

### Prizes
Organiser page language: **"cash prize, swag and extra credits"** for winners, with winners announced by Monday 24 August. **No specific dollar/pound amount was published** for this specific Gemini Edition event — do not assume a figure. (For contrast, the *previous* UK AI Agent Hackathon, EP.5 x Conduct, ran a $33,300 pool — that is a different, larger multi-day event, not this one-day Gemini Edition.)

---

## 3. Tracks, rules, submission platform

- **Track(s):** Not published in advance — organiser ground truth explicitly puts "TRACK ANNOUNCEMENT" inside the 12:15–12:30 briefing block. Nothing crawlable pins down the track(s) before that.
- **Submission platform:** Not confirmed for this specific event. UK AI Agents Lab's larger hackathons (EP.4, EP.5) used **DoraHacks** for bounties/submissions ([DoraHacks EP4 listing](https://dorahacks.io/hackathon/1985/detail)); this one-day Gemini Edition may use something lighter (a form/Devpost) — could not confirm either way.
- **Team size / IP ownership / pre-existing code rules:** **Not published anywhere found.** Neither the aiagentslab.uk hackathon page nor the Luma listing state team-size caps, whether pre-existing code/repos are allowed, or IP/ownership terms. Ask at the briefing (see §7).
- **Required artefacts (repo/video/slides):** Not stated. Given "5:30 PM hard submission deadline" and a possible demo round, assume you need at minimum a working repo/deployed link; prepare a short slide/demo script as insurance.

---

## 4. Prior editions — what's known

UK AI Agents Lab has run a series of "UK AI Agent Hackathon" editions (EP.1 through EP.5), separate from and larger than today's one-day "Gemini Edition":

| Edition | Timing | Scale (self-reported) | Partners | Notes |
|---|---|---|---|---|
| EP.1–EP.3 | since March 2025 | 330–1,200+ builders per edition | ASI Alliance (EP3) | EP3 billed as "largest Web3 × AI hackathon in Europe," 100+ projects, $100K prizes, VC follow-on from Moment Ventures, Fabric Ventures, YZi Labs, Animoca Brands ([Luma EP3 listing](https://luma.com/e2ie935t)) |
| EP.4 | ~March 2026 | — | OpenClaw (framework theme), FLock.io + Blockchain for Good Alliance ran an SDG-themed track | Billed as "world's first OpenClaw-themed university hackathon" ([RootData](https://www.rootdata.com/news/557363), [PANews](https://www.panewslab.com/en/articles/019c9df0-9a57-70ca-9d92-ab1792da39ff), [DoraHacks](https://dorahacks.io/hackathon/1985/detail)). Attempted to pull specific winner names from FLock.io's recap blog but it returned **HTTP 429 (rate-limited)** — could not confirm winning project names for EP.4.
| EP.5 x Conduct | 28 Jun – 4 Jul 2026 | $33,300 prize pool, title sponsor Conduct AI, headline sponsors Microsoft + Fetch.ai | Conduct.ai, Microsoft, Fetch.ai, OpenAI + others | Format: opening ceremony 28 Jun, mentor sessions 29 Jun–3 Jul, demo day 4 Jul, then a **House of Lords showcase in September** for selected winning teams ([aiagentslab.uk/hackathon/ep5](https://www.aiagentslab.uk/hackathon/ep5), [somo.social listing](https://somo.social/en/e/uk-ai-agent-hack-ep5-x-628)). **Winning teams/projects for EP.5 are listed on the official page as "Revealed Soon" — not yet public as of this research (22 Aug 2026).** |

**Takeaway for today:** the Lab's pattern is consistently "prize money + mentor office hours + a follow-on showcase for the best teams" (House of Lords for the flagship editions). No evidence a Gemini Edition-specific showcase/incubation follow-on exists — don't assume the House of Lords angle applies to today's event.

---

## 5. Google DeepMind's typical hackathon posture — **INFERENCE, not fact**

Everything in this section is a pattern read off *other* GDM/Google hackathons, not a statement from today's organisers about what today's judges want. Treat it as informed guidance, not a rubric.

Evidence base:
- **Gemini 3 Hackathon** (Devpost, global): stated judging weights — Technical Execution 40%, plus Impact/Innovation/Presentation. Grand Prize winner **"Globot"** — a multi-agent Gemini 3 system for supply-chain crisis response (real-time geopolitical signal monitoring → financial impact calc → route replanning) ([thenewviews.com recap](https://thenewviews.com/gemini-3-hackathon/), [Devpost rules](https://gemini3.devpost.com/rules)).
- **Gemini API Developer Competition** (2024, Google's own blog): Grand Prize **Jayu**, an AI personal assistant integrating browser/code editor/music/games with visual interpretation + real-time translation. Category winners skewed toward **accessibility** (Vite Vere — cognitive disabilities, Gaze Link — ALS eye-tracking, ViddyScribe — video audio-description) and toward **concrete vertical utility** (Prospera — sales coaching, Trippy — travel planning) over generic chatbots ([Google Developers Blog](https://developers.googleblog.com/en/announcing-the-winners-of-the-gemini-api-developer-competition/)).
- **Devpost/Google customer-story page**: notes at least one Google hackathon winner ("MLB Pitcher Mechanics Scorecard") went on to become a real business, and frames Google's preference as innovation + practical/scalable application + deep use of the specific Google stack on offer (Gemini, Vertex AI, ARCore, Flutter) ([Devpost customer story](https://info.devpost.com/customer-stories/google-hackathons-on-devpost)).

**Inference for today, given the two keynote topics (Gemini 3.7 Flash "frontier agents" and Gemma 4 "on-device"):**
- A project that **visibly and specifically uses Gemini 3.7 Flash's agentic/tool-use features** (not just a wrapper prompt) is likely to score well on "technical execution."
- A project that touches **on-device/Gemma 4** — even a small local-inference component — echoes Ian Ballantyne's talk directly and may stand out, since DevRel speakers often reward demos of exactly what they just presented.
- **Accessibility, real-world vertical utility, and multi-agent orchestration** are recurring winner shapes across GDM/Google-adjacent hackathons — a narrow, well-executed real-world use case has beaten "generic AI chatbot" ideas repeatedly.
- Expect the **live demo, not the deck**, to matter — Gemini 3 Hackathon explicitly scored a 3-minute live demo at 25%.

None of this is a confirmed rubric for the Gemini Edition — confirm actual judging criteria at 12:15.

---

## 6. NOT FOUND (explicitly unverified — do not assume)

- No published **judging criteria** for this specific event.
- No published **track list** (by design — announced at 12:15).
- No published **prize amount** in £/$ (only "cash, swag, credits").
- No confirmed **submission platform** (Devpost/DoraHacks/form — unknown).
- No confirmed **team size limit**.
- No confirmed **IP/ownership terms** or stance on pre-existing code/repos.
- No confirmed **mentor list** for today (only that GDM mentors are present 14:30–16:45).
- No confirmed **Discord/Slack specific to this event** — only the Lab's general Discord was found; a WhatsApp group was mentioned but its invite link wasn't captured.
- Could not confirm **EP.4 winning project names** (source page rate-limited, HTTP 429).
- Could not confirm **EP.5 winning project names** (organiser page states "Revealed Soon" as of today).
- Could not confirm whether a **live demo/judging round** happens for the Gemini Edition specifically (only appears in an "earlier draft schedule," per the brief's own framing).
- Speaker LinkedIn titles are taken from search-result snippets, not an opened/logged-in LinkedIn page — treat exact title wording as approximate, not verbatim.

---

## 7. Sharp questions to ask at the 12:15 briefing

1. What exactly are the track(s), and is there a rubric or weighted scoring breakdown (like the 40%-technical-execution model GDM uses elsewhere)?
2. Is there a live demo/pitch round before 17:30, or is the 17:30 deadline the entire evaluation (submission only, no stage time)?
3. What's the actual prize breakdown per place/track — and is it per-team or per-person?
4. Team size limits — solo allowed, and what's the max?
5. Is pre-existing code/starter templates allowed, or must everything be built from 12:30 onward?
6. What's the required submission artefact — repo link, deployed app, video, slides — and where do we submit (Devpost/DoraHacks/a form)?
7. Who owns the IP in submitted projects — the team, or does UK AI Agents Lab / Google DeepMind retain any rights/license?
8. Is there a follow-on opportunity for top teams (past editions had a House of Lords showcase for EP.5) — does anything similar exist for Gemini Edition winners, or is this a standalone one-day event?
9. Are Gemini 3.7 Flash API credits/quota being provided to participants today, and is there a cap?
10. Is there a specific Discord/WhatsApp channel for this event's mentor office hours (14:30–16:45), separate from the general UK AI Agents Lab Discord?

---

*Compiled 22 Aug 2026 from public web sources plus organiser-provided ground truth (see §1). Section 5 is explicitly inferential; do not present it as this event's actual rubric.*
