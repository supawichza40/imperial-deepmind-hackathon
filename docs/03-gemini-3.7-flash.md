# Gemini 3.7 Flash — working reference

Verified 2026-08-22 for the UK AI Agent Lab hackathon. Model launched **13 Aug 2026**, GA (not preview). All claims below carry an inline source; anything not confirmed against an official page is marked `UNVERIFIED`.

## Copy-paste facts

| Fact | Value | Source |
|---|---|---|
| Model ID (use in `model=`) | `gemini-3.7-flash` | [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash) |
| Status | GA / Stable (not preview) | [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash) — "Stable: `gemini-3.7-flash`" |
| Input context window | 1,048,576 tokens (~1M) | [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash) |
| Max output tokens | 65,536 (~64k) | [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash) |
| Inputs | Text, Image, Video, Audio, PDF | [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash), [DeepMind flash page](https://deepmind.google/models/gemini/flash/) |
| Outputs | Text only (no image/audio/video output) | [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash) |
| Knowledge cutoff | March 2026 (but some domains behave as Jan 2025) | [model card](https://deepmind.google/models/model-cards/gemini-3-7-flash/) |
| Thinking control param | `thinking_level`: `low` / `medium` / `high` (default `medium`); `minimal` NOT supported, errors | [what's new](https://ai.google.dev/gemini-api/docs/latest-model), [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash) |
| Price (input), through Dec 31 2026 | $0.75 / 1M tokens | [pricing page](https://ai.google.dev/gemini-api/docs/pricing) |
| Price (output, incl. thinking tokens), through Dec 31 2026 | $3.75 / 1M tokens | [pricing page](https://ai.google.dev/gemini-api/docs/pricing) |
| Price after Jan 1 2027 | $1.50 in / $7.50 out per 1M | [pricing page](https://ai.google.dev/gemini-api/docs/pricing) |
| Free tier | Free of charge (rate-limited — see §7) | [pricing page](https://ai.google.dev/gemini-api/docs/pricing) |
| Context caching | Supported, min 4,096 input tokens to trigger | [caching docs](https://ai.google.dev/gemini-api/docs/caching) |
| Computer use tool | Supported — **Preview** status | [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash), [computer use docs](https://ai.google.dev/gemini-api/docs/computer-use) |
| Current recommended SDK call | `client.interactions.create(model="gemini-3.7-flash", ...)` — new **Interactions API**, GA, supersedes legacy `generateContent` | [gemini-3 dev guide](https://ai.google.dev/gemini-api/docs/gemini-3), [function-calling docs](https://ai.google.dev/gemini-api/docs/function-calling) |

---

## 1. Model IDs / aliases

- Only one usable ID for this model: **`gemini-3.7-flash`**. The model page lists it as the sole "Versions" entry, tagged **Stable** — there is no `-preview` suffix variant for 3.7 Flash. [ai.google.dev/gemini-api/docs/models/gemini-3.7-flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash)
- Sibling models actively documented alongside it, for contrast (all in the Gemini 3 family): `gemini-3.1-flash-lite` (stable), `gemini-3.1-pro-preview` (preview), `gemini-3-flash-preview` (preview), `gemini-3.1-flash-image-preview` / `gemini-3-pro-image-preview` (Nano Banana image models, preview). [gemini-3 dev guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- `gemini-3.6-flash` is the immediate predecessor (launched ~3 weeks earlier, per press coverage) and is the documented migration source. [9to5google](https://9to5google.com/2026/08/13/gemini-3-7-flash-launch/), [what's new page](https://ai.google.dev/gemini-api/docs/latest-model)
- **API paradigm change to note**: Google's docs now front the **Interactions API** (`client.interactions.create(...)`) as GA and the recommended way to call all current models, including 3.7 Flash; the older `generateContent` endpoint is called out as legacy in several docs pages (e.g. Computer Use docs split "Gemini 2.5 (Legacy)" vs current). If you copy code samples from older tutorials or your own memory, check they use `interactions.create`, not `generateContent`. [ai.google.dev banner](https://ai.google.dev/gemini-api/docs/rate-limits), [computer-use docs](https://ai.google.dev/gemini-api/docs/computer-use)

## 2. Context window, output, cutoff, modalities

- Input token limit: **1,048,576** (~1M). Output token limit: **65,536** (~64k). [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash)
- Supported inputs: **Text, Image, Video, Audio, PDF** (PDF handled via the document-understanding path, same Files-API upload flow as images). Output modality: **Text only** — no native image/audio/video generation from this model. [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash), [DeepMind flash page](https://deepmind.google/models/gemini/flash/)
- Knowledge cutoff is stated as **March 2026** by the model card, with an explicit caveat: *"users can expect updated information for some domains while in others they may experience the model's knowledge is limited to January 2025 (in line with the Gemini 3 Model Family)."* Treat any date-sensitive fact from the model's own knowledge as unreliable without Search grounding. [model card](https://deepmind.google/models/model-cards/gemini-3-7-flash/)
- Multimodal *output* (audio generation, image generation, Live API) is explicitly **Not supported** on this model — pair with a different model (e.g. Nano Banana for images, a Live API model for realtime audio) if your agent needs those. [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash)

## 3. Thinking / reasoning controls

- Parameter name: **`thinking_level`**, values `low` / `medium` / `high`. Default for `gemini-3.7-flash` is **`medium`**. [what's new page](https://ai.google.dev/gemini-api/docs/latest-model)
- `minimal` is explicitly **not supported** for this model and returns an API error if passed. [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash)
- The older `thinking_budget` parameter (token-count based) still works for backward compatibility, but Google recommends migrating to `thinking_level` for more predictable behavior, and warns not to set both in the same request. [gemini-3 dev guide FAQ](https://ai.google.dev/gemini-api/docs/gemini-3)
- Example call shape:
  ```python
  interaction = client.interactions.create(
      model="gemini-3.7-flash",
      input="...",
      generation_config={"thinking_level": "low"},
  )
  ```
  [gemini-3 dev guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- Output pricing is billed **including thinking tokens** — a `high` thinking level directly raises your output-token bill. [pricing page](https://ai.google.dev/gemini-api/docs/pricing)

## 4. Pricing, cached-input pricing, free tier

Official "Standard" tier pricing for `gemini-3.7-flash` from the [pricing page](https://ai.google.dev/gemini-api/docs/pricing):

| | Free Tier | Paid Tier (per 1M tokens, USD) |
|---|---|---|
| Input | Free of charge | $0.75 through Dec 31 2026 → $1.50 from Jan 1 2027 |
| Output (incl. thinking tokens) | Free of charge | $3.75 through Dec 31 2026 → $7.50 from Jan 1 2027 |
| Context caching (per-token) | Free of charge | $0.075 through Dec 31 2026 → $0.15 from Jan 1 2027 |
| Context caching (storage, per hour) | Free of charge | $0.50/1M tokens/hr through Dec 31 2026 → $1.00/1M tokens/hr from Jan 1 2027 |
| Google Search grounding | Not available | 5,000 free requests/month (shared across all Gemini 3.x models), then $14/1,000 |
| Google Maps grounding | Not available | 5,000 free/month (shared across Gemini 3.x), then $14/1,000 |
| Data used to improve Google's products | Yes (free tier) | No (paid tier) |

**Important:** this is explicitly an *introductory* price — half the prior 3.6 Flash rate — and it **doubles on 1 January 2027**. Don't build a cost model past that date off today's numbers. [Google blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/), [pricing page](https://ai.google.dev/gemini-api/docs/pricing)

Context caching kicks in automatically (implicit caching, on by default for Gemini 2.5+ models) once a request's cacheable prefix hits **4,096 input tokens** for Gemini 3.7 Flash — smaller prompts never get the cache discount. Cache hit count is visible in `usage.total_cached_tokens`. Note the Interactions API only supports *implicit* caching; explicit/manual cache objects require the older `generateContent` API. [context caching docs](https://ai.google.dev/gemini-api/docs/caching)

Free-tier RPM/TPM/RPD **specific to `gemini-3.7-flash`** could not be confirmed from a dynamically-rendered rate-limits table at fetch time — the official [rate-limits page](https://ai.google.dev/gemini-api/docs/rate-limits) tells you to check **your live limits in AI Studio** (`aistudio.google.com/rate-limit`) rather than relying on a static number, since limits depend on usage tier and account history. `UNVERIFIED` for exact numbers on 3.7 Flash specifically — sibling Flash models (e.g. Gemini 3 Flash, Gemini 2.5 Flash) have historically sat around 10–15 RPM / ~250k TPM / 500–1,500 RPD on the free tier, but do not assume 3.7 Flash matches this without checking your own AI Studio dashboard. [rate-limits page](https://ai.google.dev/gemini-api/docs/rate-limits)

Spend-based rate limits (apply regardless of RPM/TPM, evaluated on a rolling 10-minute window):

| Usage tier | Spend limit per 10 min |
|---|---|
| Free | N/A |
| Tier 1 | $10 |
| Tier 2 | $50 |
| Tier 3 | $200 |

Hitting this returns `429 RESOURCE_EXHAUSTED` even if you're under RPM/TPM. [rate-limits page](https://ai.google.dev/gemini-api/docs/rate-limits)

## 5. Latency/throughput and when to pick Flash vs Pro vs Flash-Lite vs Gemma

Per Google's own "Meet the Gemini 3 series" table, the family lineup and per-1M-token pricing (input/output) is:

| Model ID | Context (in/out) | Cutoff | Price in/out |
|---|---|---|---|
| `gemini-3.1-flash-lite` | 1M/64k | Jan 2025 | $0.25 (text/image/video), $0.50 (audio) / $1.50 |
| `gemini-3.7-flash` | 1M/64k | Mar 2026 | $0.75 / $3.75 (intro, through Dec 2026) |
| `gemini-3.1-pro-preview` | 1M/64k | Jan 2025 | $2/$12 (<200k ctx), $4/$18 (>200k ctx) |
| `gemini-3-flash-preview` | 1M/64k | Jan 2025 | $0.50/$3 |

[gemini-3 dev guide](https://ai.google.dev/gemini-api/docs/gemini-3), [pricing page](https://ai.google.dev/gemini-api/docs/pricing)

Rule of thumb for picking, per Google's own framing plus DeepMind's product page:

- **Gemini 3.7 Flash** — "our most intelligent workhorse model yet for coding and agents"; DeepMind's page literally tags it "Best for tackling complex agentic tasks at scale." This is the default pick for a hackathon agent: coding, tool-calling, multi-step workflows, computer use. [DeepMind flash page](https://deepmind.google/models/gemini/flash/), [Google blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/)
- **Gemini 3.1 Pro** — pick when a task genuinely needs the deepest reasoning / broadest world knowledge and you can tolerate higher latency and ~3x the cost. [gemini-3 dev guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- **Gemini 3.1 Flash-Lite** — cheapest, described as "our workhorse model built for cost-efficiency and high-volume tasks" — good for classification/routing/pre-filter steps ahead of a Flash or Pro call. [gemini-3 dev guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- **Gemma 4** — an open-weights model you run yourself, not a hosted Gemini API model. No per-token API cost, runs locally/offline, but ceiling is bounded by your own hardware rather than cloud scale. Third-party benchmarking cites Gemini Flash-tier models generating roughly an order of magnitude faster token throughput than local Gemma 4 on typical hardware. `UNVERIFIED` (numbers from an aggregator benchmarking site, not Google): [artificialanalysis.ai comparison](https://artificialanalysis.ai/models/comparisons/gemma-4-31b-vs-gemini-3-1-flash-lite-preview).

Independent benchmark press coverage (not from Google, cross-check before quoting in a pitch deck):
- DeepSWE v1.1 (software engineering): Gemini 3.7 Flash 65.3%, up from 3.6 Flash's 49.0%; GPT-5.6 Terra leads at 69.6%. [officechai.com](https://officechai.com/ai/gemini-3-7-flash-benchmarks/)
- AutomationBench (Zapier's enterprise workflow-automation benchmark): Gemini 3.7 Flash 30.4%, up from 3.6 Flash's 17.0%, ahead of GPT-5.6 Terra (23.6%) and Claude Sonnet 5 (10.7%). [officechai.com](https://officechai.com/ai/gemini-3-7-flash-benchmarks/)
- "Harbor-Index" agent benchmark numbers referenced in some coverage could not be independently confirmed from a primary source — `UNVERIFIED`.

No official first-party latency/tokens-per-second numbers for 3.7 Flash were found in Google's own docs at fetch time — treat any specific "X tokens/sec" figure you see in third-party posts as `UNVERIFIED` for this exact model (one such figure found in search results was actually reported for the *predecessor* 3.6 Flash, not 3.7).

## 6. What's genuinely new vs Gemini 3.6 Flash (agent-relevant)

- Marketed explicitly as "our most intelligent workhorse model yet for **coding and agents**" — the positioning itself shifted more toward agentic/coding vs. general chat. [Google blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/)
- Adapts better to roadblocks mid-task, asks for clarification when intent is ambiguous, and follows instructions with higher fidelity — all direct agent-loop-reliability improvements. [Google blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/)
- Debugging and issue-resolution gains, higher first-pass code accuracy, more production-ready code output. [Google blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/)
- Web development: generates more functional layouts and feature-complete apps in fewer prompts (fewer round-trips = fewer tokens/time for a hackathon build loop). [Google blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/)
- **Computer use tool** is available on this model (`"type": "computer_use"`, `environment: "desktop"` or `"mobile"`) — lets the agent drive a real UI (click, type, scroll) with a `safety_decision`/`safety_acknowledgement` confirmation loop for risky actions, and supports excluding specific predefined actions or adding a custom `yield_to_user` escape-hatch tool so the agent can hand control back to a human. Status is **Preview**, not GA. This is the most directly hackathon-relevant "new" capability for anyone building a browser/desktop-driving agent. [computer-use docs](https://ai.google.dev/gemini-api/docs/computer-use)
- Full built-in tool roster on this model: function calling, Google Search grounding, Google Maps grounding, file search, code execution, URL context, computer use (preview), structured outputs, Batch API, Flex inference, Priority inference. Not supported: audio generation, image generation, Live API. [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash)
- Price is literally half of 3.6 Flash's rate during the introductory window — makes heavier agent loops (many tool calls, long multi-step chains) markedly cheaper to run for the duration of the promo. [VentureBeat](https://venturebeat.com/technology/googles-gemini-3-7-flash-targets-coding-and-agents-with-a-50-introductory-price-cut), [MarkTechPost](https://www.marktechpost.com/2026/08/13/google-ai-just-released-gemini-3-7-flash/)

Note on the "Frontier Agents with Gemini 3.7 Flash" keynote by Amit Vadi referenced in the task brief: I could not find an independent public source confirming this specific keynote/speaker — that detail is `UNVERIFIED` (may be a hackathon-local/internal announcement not indexed on the open web). Everything else about the model itself above is independently confirmed from Google's own docs/blog/model card, which is the important part for building against it.

## 7. Known limitations, gotchas, rate-limit traps

1. **Knowledge cutoff is inconsistent by domain.** Card says March 2026 but warns some domains behave as if capped at January 2025. Don't trust the model's unaided knowledge for anything recent — wire up Search grounding (`{"type": "google_search"}` tool) for current events. [model card](https://deepmind.google/models/model-cards/gemini-3-7-flash/)
2. **`thinking_level: "minimal"` errors out** on this model — only `low`/`medium`/`high` are valid, unlike some other Gemini models that accept `minimal`. [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash)
3. **Computer use is Preview, not GA** — expect rougher edges, and you must implement the `safety_decision`/`safety_acknowledgement` confirmation flow or risky actions (e.g. data-modifying steps) will be blocked. [computer-use docs](https://ai.google.dev/gemini-api/docs/computer-use)
4. **No native image/audio/video output.** If your demo needs generated images (e.g. a UI mockup, a diagram) or spoken output, you need a second model call (Nano Banana for images, a Live API/TTS model for audio) — plan the extra API call/cost into your architecture now, not during the demo. [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash)
5. **API surface has moved to the Interactions API** (`client.interactions.create`). Older `generateContent`-style code (including possibly your own training-data muscle memory) is now "legacy" in Google's own docs for some features (e.g. computer use, explicit caching). Mixing old and new patterns in the same client session is a common source of confusing errors — pick one and stay consistent. [rate-limits page banner](https://ai.google.dev/gemini-api/docs/rate-limits), [computer-use docs](https://ai.google.dev/gemini-api/docs/computer-use)
6. **Price is an introductory rate.** It doubles automatically on 1 Jan 2027 — irrelevant for a one-day hackathon, but don't reuse today's numbers in any longer-term cost projection you might reuse later. [pricing page](https://ai.google.dev/gemini-api/docs/pricing)
7. **Spend-based rate limiting can 429 you even under RPM/TPM limits** if you're on a paid tier and burn through $10/$50/$200 in a rolling 10-minute window (Tier 1/2/3 respectively) — a plausible failure mode if multiple team members hammer the API in parallel during a crunch. [rate-limits page](https://ai.google.dev/gemini-api/docs/rate-limits)
8. **Exact free-tier RPM/TPM/RPD for `gemini-3.7-flash` isn't nailed down in the static docs** — Google explicitly tells you to check your live limits in AI Studio rather than assume a fixed number, since it depends on usage tier/account history. Check `aistudio.google.com/rate-limit` early, not mid-demo. [rate-limits page](https://ai.google.dev/gemini-api/docs/rate-limits)
9. **Context caching needs a 4,096-token floor** on the input to trigger automatically — short prompts (typical for quick tool-call round trips) won't be cached, so don't expect caching to save costs on chatty short-turn agent loops. [caching docs](https://ai.google.dev/gemini-api/docs/caching)
10. **Google Search / Maps grounding free quota (5,000 requests/month) is shared across all Gemini 3.x models**, not per-model — if your team runs several Gemini 3.x models with grounding simultaneously, you're drawing from one shared pool. [pricing page](https://ai.google.dev/gemini-api/docs/pricing)
