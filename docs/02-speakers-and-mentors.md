# Hackathon Speakers & Mentors Dossier

**Event:** UK AI Agent Lab: Gemini Edition | DeepMind x Google  
**Date:** Friday, 22 August 2026  
**Compiled:** Quick reference for in-person conversations

---

## 1. AMIT VADI
**Title:** Head of Community, Google DeepMind Developer Experience  
**X:** @vadiamit | **Location:** London

### Public Profile
(organiser-supplied) Leads developer go-to-market and community enablement for the Gemini API and Google AI Studio at GDM. Drives developer adoption across startup ecosystems, incubators, accelerators. Previously 9 years at Apple (worldwide product marketing/programs), 2 years scaling developer programs and web3 platforms.

**Verified via:** [LinkedIn](https://uk.linkedin.com/in/amitvadi) · [X @vadiamit](https://x.com/vadiamit) · Google DeepMind Gemini Builders event series

### What He Cares About
- **Developer adoption** at scale — startups, ecosystems, accelerators
- **Ecosystem velocity** — making it frictionless for builders to ship
- **Startup success** — has spoken at CTO Connect events (Copenhagen 2026, Stockholm 2026) specifically for startup CTOs
- **Community enablement** — not just documentation but human-to-human programs
- **Resilience & building** — recent X post: "2025 has truly been one for the books... a year of challenges, yes, but also of incredible resilience and innovation"

### Recent Themes
- Gemini API adoption in startup ecosystems
- Gemini 3.7 Flash for frontier agents (keynote theme: "Research to Reality with Google DeepMind")
- Developer programs that unlock deployment at scale

### What Would Impress Him
- A product that lowers the barrier to entry for developers (not another SOTA model demo)
- Evidence of **how fast it gets to production** — deployment, iteration speed
- Community/network effects — "how does this spread through builders?"
- Solving a real problem for startups (cost, speed, maintenance)
- Clear path from prototype to revenue/traction

### 5 Sharp Questions to Ask Amit
1. **What's the most common reason a promising startup's AI project stalls after the initial build?** (He'll likely surface real friction points — tooling, infra, cost, or team expertise)
2. **You've scaled developer programs at Apple and in web3. What's the biggest difference in how startups adopt Gemini vs. how they adopted those platforms?**
3. **Which startup use cases for Gemini agents are you NOT seeing yet that you think are obvious?** (Shows his gap-spotting)
4. **For a team of 3-4 builders with zero Go-to-Market experience, what's the single most expensive mistake you see them make in the first 90 days?**
5. **How are you thinking about the cost of inference vs. developer productivity? Is cost the constraint, or is it something else right now?** (Might reveal what's actually blocking adoption)

### 30-Second Pitch to Amit
*"We built [X use case] because we noticed [specific friction point in developer workflow]. We validated it with [N] builders/startups and hit [metric]. We're shipping with Gemini agents because [why specifically Gemini, not alternative]. The thing that makes us different: [unfair advantage for speed/cost/adoption]. What we need most right now: [specific blocker — mentorship, users, infrastructure input]."*

**Tone:** Startup operator, not student. Assume he knows the DevX game. Lead with the friction you solved and evidence you validated it.

---

## 2. IAN BALLANTYNE
**Title:** Gemma DevX Lead, Google DeepMind Developer Experience  
**X:** @IanBallantyne (also @ianerballantyne) | **Location:** London

### Public Profile
(organiser-supplied) Leads technical developer experience and open-weights enablement for Gemma. Focus: on-device intelligence, parameter-efficient fine-tuning (PEFT/LoRA), fast/private/localized agentic systems with Gemma 4.

**Verified via:** [LinkedIn posts on Gemini 2.0 & Gemma](https://www.linkedin.com/in/ianballantyne) · [YouTube: "Sovereign Escape Velocity: Ownership w Open Models"](https://www.youtube.com/watch?v=SS-A8sE7hkw) with Gus Martins · [GDG Imperial College talk: "AI Horizons with Ian Ballantyne"](https://gdg.community.dev/events/details/google-gdg-on-campus-imperial-college-london-london-united-kingdom-presents-ai-horizons-a-conversation-with-ian-ballantyne-from-google-deepmind/) · Google Developers Blog

### What He Cares About
- **Open-weights models as a path to sovereignty** — "Ownership with Open Models" is a recurring theme
- **On-device AI as the default** — privacy, latency, control, cost
- **Practical deployment**, not papers — he demos Gemma 4 multi-agent systems running live (e.g., "Gemma Playground: Parallel Agents in Action" on YouTube)
- **Builders' autonomy** — the ability to fine-tune, customize, and own your intelligence layer
- **Edge runtimes** — LiteRT-LM, quantization, serving engines that ship on consumer hardware

### Recent Themes
- Gemma 4 (2B, E2B, E4B, 26B MoE, 31B Dense) — multimodal, agentic-first
- Local-first intelligence: **LiteRT-LM for on-device inference**, **AI Edge Gallery**, **Qualcomm QNN integration**
- Multi-agent orchestration at the edge — spinning up 10 independent subagents on Gemma 4
- Privacy-first workflows: agents that never leave your device
- Specialized weights for domain-specific tasks (medical, etc.)

### What Would Impress Him
- A working **on-device agentic system** (doesn't need to be huge — E2B/E4B running locally is enough)
- **Quantization or PEFT trick** that unlocks something meaningful (new model capability, speed, memory efficiency)
- Evidence that **users control their own intelligence** — show sovereignty, not vendor lock-in
- Real **multi-agent orchestration** — not just RAG, actual parallel subagents solving a problem
- A use case where **on-device beats cloud** on latency, cost, or privacy (he lives for these)

### 5 Sharp Questions to Ask Ian
1. **Gemma 4 E2B fits in 1.5GB. What's the biggest surprise you've had about what that model can actually do once people have it locally?**
2. **You could push Gemma to the cloud and scale infinitely. Why do you personally believe on-device AI matters more than convenience?** (Forces him to articulate the real problem)
3. **PEFT and LoRA are old techniques. What's different about fine-tuning Gemma vs. fine-tuning proprietary models in terms of speed or quality?**
4. **If I have a specialized use case (medical, legal, domain-specific), is Gemma 4 the right base, or should I be looking at something else? How do you advise builders on that choice?**
5. **Parallel agents on the edge — how do you think about deadlock, failure handling, and state consistency when everything is decentralized and local?** (Deep technical question; shows you understand orchestration)

### 30-Second Pitch to Ian
*"We're building a [domain-specific use case] that required on-device intelligence because [privacy / latency / cost bottleneck]. We fine-tuned Gemma 4 E4B with [LoRA / PEFT technique] and achieved [performance metric]. It now runs on [device type — phone, laptop, embedded] without degradation. Key insight: [why Gemma specifically solved this, not alternatives]. What we're stuck on: [inference performance / serving / quantization / orchestration challenge]."*

**Tone:** Technical builder. He respects hard problems and quantitative evidence. Don't claim magic; show numbers. He's seen too many "AI magic" pitches.

---

## 3. DENISH KC
**Title:** AI GTM Lead, Google Cloud AI Team  
**Location:** London | **Background:** Imperial College London (Dean's Scholarship), CFA Level 1

### Public Profile
(organiser-supplied) AI GTM (go-to-market) Lead @ Google. [LinkedIn: Denish KC](https://uk.linkedin.com/in/denishkc) Partnering with strategic UK scaleups on AI Models.

**Verified via:** [LinkedIn profile](https://uk.linkedin.com/in/denishkc) · Keynote speaker at UCL School of Management "AI and the Future of Business" · Active in Fetch.ai Innovation Lab

### What He Cares About
- **Enterprise AI adoption** — how do scaleups actually use Gemini in production?
- **Go-to-market strategy for AI** — sales enablement, positioning, competitive angles
- **Agents as a business shift** — not incremental, but paradigm-change for how work gets done
- **UK startup ecosystem** — he's explicitly focused on UK scaleups as partner companies
- **Business transformation, not just technology** — talks about agents as the "agent leap" that redefines enterprise workflows

### Recent Themes
- **Shift from chatbots to agents** — enterprises are moving beyond Q&A to autonomous decision-making
- **Agent-native interfaces** — how to architect GTM for agentic systems
- **AI agent trends 2026** — orchestration, reliability, enterprise trust
- **Gemini for enterprise** — competitive positioning vs. competitors

### What Would Impress Him
- A **production-grade agent system** that's already deployed with real users/revenue
- Clear **business metrics** — cost savings, time saved, revenue impact, not just technical elegance
- **Defensibility story** — why would a customer stick with this vs. building it themselves or using a competitor?
- Evidence of **enterprise-grade reliability** — error handling, monitoring, user trust
- A use case that shows **how agents reshape a workflow**, not just speed it up

### 5 Sharp Questions to Ask Denish
1. **What's the difference between an AI solution that impresses a CTAs and one that actually gets bought by enterprise procurement?** (He'll reveal hidden GTM constraints)
2. **You're working with UK scaleups. What's the most common reason they say "yes" to Gemini agents vs. OpenAI or Anthropic?"**
3. **If I have a working agent today, what's the fastest way to get enterprise customers to try it — and what do they actually care about in the first conversation?**
4. **The "chatbot to agents" shift is real. But are enterprises actually adopting agents, or are they still stuck on RAG + retrieval?" (Reveals where the adoption gap really is)
5. **For a startup pitching to enterprise CIOs, how much should they lead with "runs on Gemini" vs. the business outcome?** (Tests what positioning actually sells)

### 30-Second Pitch to Denish
*"We built an agent for [enterprise workflow — e.g., customer support, procurement, operations] and deployed it with [N] companies. They're seeing [concrete business metric: cost reduction, FTE hours saved, revenue impact]. The competitive advantage: [why customers picked us]. What we need from Google: [co-selling intro, feature request for Gemini, positioning help, or enterprise customer intros]."*

**Tone:** GTM operator. Don't start with tech; start with the customer problem and the business outcome. He's evaluating your pitch on **sellability**, not novelty.

---

## MENTOR OFFICE HOURS: Smart Protocol
**Time:** 14:30-16:45 today  
**Mentors:** Google DeepMind team (incl. Amit, Ian, and others)

### What to Bring
- **Live demo** (laptop, phone, tablet — whatever shows your work): 30-60 seconds of walking through the actual system
- **One specific blocker** (not vague): infrastructure, model choice, deployment, cost, GTM, user validation
- **Metric or North Star**: what are you optimizing for? (latency, cost, user retention, deployment speed, accuracy)
- **Decision you need help with** (optional but highest value): "Should we fine-tune vs. prompt? Should this be on-device or cloud?"

### What to Ask
**High-value questions:**
- "We're stuck on [specific blocker]. Here's what we've tried. What would you try next?"
- "Is there a pattern or lesson from other teams you mentored that applies to our problem?"
- "What feature from Gemini or Gemma would unlock this, and is it on the roadmap?"
- "How do you think about this trade-off? [latency vs. cost / on-device vs. cloud / speed to market vs. polish]"

**Lower-value questions (save for live):**
- "How do I get started with Gemini?" (docs are better than office hours)
- "Can you review my code?" (too fine-grained; use your peers)
- "What's new in Gemini 3.7?" (they'll cover this in talks)

### What NOT to Do
- Don't pitch; **problem-solve together**. They want to see the friction and help you ship.
- Don't ask for intros or funding (wrong channel; use social after)
- Don't monopolize time if there's a queue — be crisp (5-7 min), then yield to the next team
- Don't ask permission; ask for advice on a decision you've already scoped

### Sample Script (2 minutes)
*"Hi! We built a [system] using Gemma 4 for [use case]. Our North Star is [metric]. We're blocked on [blocker]. Here's our current approach: [brief]. The trade-offs we're weighing: [two options]. What would you recommend?"*

Then listen, ask a follow-up, and leave with an action item.

---

## Quick Reference: What Each Speaker Wants from Your Pitch

| Speaker | Lead With | Back Up With | Avoid |
|---------|-----------|-------------|-------|
| **Amit** | How fast it gets to production | Startup validation / customer traction | Academic claims, vague "impact" |
| **Ian** | On-device demo or quantization insight | Technical depth (PEFT, serving, latency) | Cloud-only or proprietary-only pitch |
| **Denish** | Business metric (cost saved, FTE, revenue) | Customer reference or pilot data | "Uses Gemini" without the why |

---

## Sources
- [Amit Vadi LinkedIn](https://uk.linkedin.com/in/amitvadi)
- [Amit Vadi on X](https://x.com/vadiamit)
- [Ian Ballantyne YouTube: Sovereign Escape Velocity](https://www.youtube.com/watch?v=SS-A8sE7hkw)
- [Ian Ballantyne: AI Horizons (GDG Imperial)](https://gdg.community.dev/events/details/google-gdg-on-campus-imperial-college-london-london-united-kingdom-presents-ai-horizons-a-conversation-with-ian-ballantyne-from-google-deepmind/)
- [Denish KC LinkedIn](https://uk.linkedin.com/in/denishkc)
- [Gemma 4 Technical Features & LiteRT (Medium)](https://medium.com/@njiang.pin/on-device-ai-on-android-in-2026-what-gemma-4-means-for-your-tflite-classifiers-ffb349e9e28f)
- [LiteRT-LM & On-Device GenAI (Google Developers Blog)](https://developers.googleblog.com/blazing-fast-on-device-genai-with-litert-lm/)
- [Gemma 4 & Multimodal AI (Medium GDE)](https://medium.com/google-developer-experts/bringing-multimodal-gemma-4-e2b-to-the-edge-a-deep-dive-into-litert-lm-and-qualcomm-qnn-4e1e06f3030c)
- [CTO Connect with DeepMind (Google Cloud)](https://cloud.google.com/events/cto-connect-with-deepmind/google-stockholm)
