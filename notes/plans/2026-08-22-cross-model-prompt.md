# Paste-ready brief — hackathon idea search (Grok / Cursor / any external model)

Paste everything below the line. Nothing above it.

---

You are helping a small team win a one-day hackathon **today**. Give me candidate product ideas, not encouragement.

## The event (facts, not guesses)

- **UK AI Agent Lab: Gemini Edition**, run with Google DeepMind. London, Saturday 22 August 2026.
- **Build window: 12:30 → 17:30, minus a 1-hour lunch ≈ 4 hours net.** Plan for **3h build + 45min deploy and demo polish + 15min submission buffer**.
- **The track is announced at 12:15 and is not public yet.** So do not give me one idea. Give me a portfolio spread across life domains, each one re-skinnable to a different track.
- Judges: Google DeepMind DevRel. This morning's keynotes were **Gemini 3.7 Flash agentic tool use** (Amit Vadi) and **Gemma 4 on-device / local-first** (Ian Ballantyne). Speakers reward demos of what they just presented.
- Comparable Google rubrics weigh: **technical execution 25–50%, innovation 20–30%, demo/presentation 10–20%**, plus an explicit "did you use Gemini/Gemma meaningfully" line item. A build that could have run on any LLM forfeits a whole category.
- Judges spend **90 seconds to 3 minutes** per project and physically click through it. What they can perceive beats what they cannot.
- Submission needs a **public link that does not require a login**. A localhost demo scores as broken.
- Free-tier Gemini is **~15 requests per minute**. Venue wifi is unreliable.

## What I want

**8 candidate ideas**, each buildable by a small Python-and-web team in 3 hours, each **useful to an ordinary adult multiple times a week** (not a tool for developers, not a tool for a niche profession), and each **not already a shipped product**.

Google surfaces you may build on: Gemini 3.7 Flash (agentic multi-step tool calling, function calling, multimodal, thinking levels), the Interactions API, Gemini computer-use (preview), Gemma 4 running locally on-device (multimodal, LiteRT, private/offline), ADK / A2A for multi-agent, Google AI Studio. Note: **Antigravity is a coding tool, not a product surface** — using it is a story about how fast we shipped, never the novelty of the idea itself.

## Hard filters — apply these before you write an idea down

1. **Prior art.** Name the closest thing that already exists (product, app, GitHub repo, Devpost entry) and state the specific delta. If you cannot name the closest existing thing, you have not looked. "I'm not aware of one" is a fail.
2. **Frequency.** State how many times a week an ordinary adult hits this problem and why you believe that. A great tool used twice a year loses to a mediocre one used daily.
3. **The 90-second wow.** Describe the single moment a judge sees. Better if a **judge supplies the input** live ("say any sentence", "hand it any receipt") — canned flows read as rehearsed.
4. **No third-party OAuth.** Gmail/bank/calendar consent screens burn an hour and fail on a judge's laptop. Prefer paste-in, file upload, camera, microphone, or public data.
5. **Survives 15 RPM and dead wifi.** Say what happens when the API throttles. On-device Gemma 4 as fallback is worth extra points, not just insurance.
6. **One golden path.** One feature, done properly. Multiple half-finished features lose to one polished workflow, every judging writeup says so.
7. **No medical, legal, or financial advice claims.** Judges poke exactly there.
8. **Anti-template.** Auto-reject: "AI assistant for X", chat-wrapper-over-your-documents, generic RAG, another meeting summariser, another resume tailor. Standouts depart furthest from the template.
9. **Deployable to a public URL inside the window.** Say how.
10. **The quotable number.** One before/after a judge can repeat to the next judge unaided: "cut a 45-minute task to 60 seconds."

## Output format — one block per idea, no preamble, no summary paragraph

```
IDEA n — <name>
Problem in one sentence (a person's words, not a market description):
Who and how often:            <frequency claim + why you believe it>
The 90-second wow:            <exactly what the judge sees, and what they type or say>
Google feature named out loud: <which one, and why this idea genuinely needs it>
Closest existing thing:       <name + link> — Delta: <what is actually new>
Build in 3h:                  <file list / stack / the riskiest 20 minutes>
When the API throttles:       <fallback>
Quotable number:              <before → after>
Which track it fits:          <agents / on-device / accessibility / productivity / creative / safety>
Kill risk:                    <the single most likely reason this fails on stage>
```

Rank them at the end, best first, one line of reasoning each. Be blunt about the weak ones — I would rather lose an idea now than at 16:00.
