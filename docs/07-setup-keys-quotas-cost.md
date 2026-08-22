# Setup, Keys, Quotas & Cost — Survival Guide

**Event:** UK AI Agent Lab: Gemini Edition (Google DeepMind), London, 22 Aug 2026. Hack 12:30–17:30.
**Goal of this doc:** get every team member from zero to a working Gemini API call in under 10 minutes, then not get blindsided by a 429 or a surprise bill.

> **First thing to do, before reading anything else:** ask an organiser/DeepMind volunteer if there's an event-specific API key, promo code, or quota bump for today. DeepMind-run hackathons commonly hand these out on the day — it's higher-leverage than anything in the "Credits" section below and isn't something we can verify by web search. *(Recommendation, not a sourced fact.)*

---

## 0. TL;DR — do this now

- [ ] Go to **https://aistudio.google.com/api-keys**, sign in, click **Create API key**. No credit card, no billing account needed for the free tier. [[source]](https://ai.google.dev/gemini-api/docs/api-key)
- [ ] Export it as `GEMINI_API_KEY` (see §1.2 for exact commands).
- [ ] `pip install -U -q "google-genai"` (Python) or `npm install @google/genai` (Node/TS). [[source]](https://ai.google.dev/gemini-api/docs/migrate)
- [ ] Run the hello-world snippet in §2. If you get text back, you're live.
- [ ] Default model choice for the day: **`gemini-2.5-flash`** — stable (not preview), free tier, cheap, good enough for almost everything. `gemini-3.7-flash` (launched **13 Aug 2026**, GA, most capable Flash model) is also free-tier eligible and worth it if you need stronger coding/agent performance. [[source]](https://9to5google.com/2026/08/13/gemini-3-7-flash-launch/) [[source]](https://ai.google.dev/gemini-api/docs/latest-model)
- [ ] **Use the Interactions API (`client.interactions.create`), not `generateContent`, for new code.** Google's own docs now bannner every rate-limits/quickstart page with *"The Interactions API is now generally available. We recommend using this API for access to all the latest features and models,"* and the old endpoint's own page is now titled **"Gemini Generate Content API (Legacy)."** It reached GA on 22 June 2026. See §2. [[source: banner, live-fetched]](https://ai.google.dev/gemini-api/docs/rate-limits) [[source: legacy page title]](https://ai.google.dev/gemini-api/docs/generate-content/get-started) [[source: GA announcement]](https://blog.google/innovation-and-ai/technology/developers-tools/interactions-api-general-availability/)
- [ ] If your demo will be used by real end users physically in the UK/EU/Switzerland (not just you, testing), read the callout in §3.4 — the free tier is not legally usable for that.

---

## 1. Getting an API key from Google AI Studio

### 1.1 Exact steps
1. Go to **[aistudio.google.com/api-keys](https://aistudio.google.com/api-keys)** and sign in with a Google account (18+, age-verified — see §7). [[source]](https://ai.google.dev/gemini-api/docs/available-regions)
2. Click **Create API key**.
   - If you're a brand-new user, AI Studio silently creates a default Google Cloud project for you and issues the key against it — you don't need to touch the Cloud Console. [[source]](https://ai.google.dev/gemini-api/docs/api-key)
   - If you already have a Google Cloud account/project, AI Studio does **not** auto-create a project — you'll be asked to import an existing one. [[source]](https://ai.google.dev/gemini-api/docs/api-key)
3. Copy the key. That's it — **you are on the free tier already, no billing account required.** [[source]](https://ai.google.dev/gemini-api/docs/rate-limits) (Free tier qualification = "active project or free trial", no billing entry.)
4. **Only needed if you want higher rate limits (paid tier):** on the API Keys or Projects page, click **Set up billing**, link/create a Cloud Billing account, add a payment method, and prepay a minimum of **$10**. [[source]](https://ai.google.dev/gemini-api/docs/quickstart)

If "Create API key" is greyed out with *"You do not have permission to create a key in this project"*, either ask your Cloud project/org admin for the `apikeys.keys.create` + `serviceusage.services.enable` permissions, or just spin up a fresh Google Cloud project with no organisation attached and create the key there. [[source]](https://ai.google.dev/gemini-api/docs/api-key)

### 1.2 The env var: `GEMINI_API_KEY` vs `GOOGLE_API_KEY`
Both work. **If both are set, `GOOGLE_API_KEY` wins.** [[source]](https://ai.google.dev/gemini-api/docs/api-key) — pick one and be consistent across your team so nobody's laptop silently reads a different key.

```bash
# macOS/Linux — add to ~/.bashrc or ~/.zshrc, then `source` it
export GEMINI_API_KEY="<your key>"
```
[[source]](https://ai.google.dev/gemini-api/docs/api-key)

```powershell
# Windows PowerShell
setx GEMINI_API_KEY "<your key>"
```
(standard Windows env-var mechanism; the docs give OS-specific tabs at the same [source](https://ai.google.dev/gemini-api/docs/api-key))

### 1.3 Security — do not skip
- **Never commit the key to git**, never hardcode it in client-side/browser JS, never paste it into a shared Slack/Discord in plaintext. [[source]](https://ai.google.dev/gemini-api/docs/api-key)
- In production, calls must go through **your own backend**, which holds the key — a browser calling `generativelanguage.googleapis.com` directly with an embedded key is extractable by anyone who opens dev tools. The Node SDK's own docs put this in a `[!CAUTION]` block. [[source]](https://www.npmjs.com/package/@google/genai)
- Optional hardening for a demo you'll show publicly: restrict the key by IP address in the [Cloud Console Credentials page](https://console.cloud.google.com/apis/credentials). [[source]](https://ai.google.dev/gemini-api/docs/api-key)

---

## 2. SDK install + hello world

### ⚠️ Important: the API surface changed in 2026 — there are now two ways to call it
As of today, Google's docs lead with a new **Interactions API** (`client.interactions.create` / `POST /v1beta/interactions`), which is **stateful by default** (multi-turn history is tracked server-side via `previous_interaction_id`) — it supersedes the older stateless `generateContent`. [[source]](https://ai.google.dev/gemini-api/docs/migrate-to-interactions) [[source]](https://ai.google.dev/gemini-api/docs/quickstart)

The classic `models.generateContent` call **still works and is still documented** (and is the *only* thing the Batch API currently supports — see §4.2), so both are shown below. For a simple hackathon script, either is fine; if you're building multi-turn chat/agent behaviour, prefer `interactions.create` since it saves you from managing chat history yourself.

### 2.1 Python
```bash
pip install -U -q "google-genai"
```
[[source]](https://ai.google.dev/gemini-api/docs/migrate)

```python
from google import genai

client = genai.Client()  # reads GEMINI_API_KEY / GOOGLE_API_KEY automatically

# Classic, stateless call
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Tell me a story in 100 words.",
)
print(response.text)

# New, stateful Interactions API
interaction = client.interactions.create(
    model="gemini-2.5-flash", input="Tell me a joke."
)
print(interaction.output_text)
```
[[source: generate_content]](https://ai.google.dev/gemini-api/docs/migrate) [[source: interactions.create]](https://ai.google.dev/gemini-api/docs/migrate-to-interactions)

**Old package alert:** if you or a teammate finds a tutorial using `import google.generativeai as genai` (package name `google-generativeai`) — that's the pre-2025 SDK. Google's own migration guide walks the old→new mapping; use `google-genai` (`from google import genai`) for anything you write today. [[source]](https://ai.google.dev/gemini-api/docs/migrate) *(We could not find an explicit sunset/EOL date for `google-generativeai` in the docs — mark as UNVERIFIED, but don't start new code on it regardless.)*

### 2.2 Node / TypeScript
```bash
npm install @google/genai
```
[[source]](https://ai.google.dev/gemini-api/docs/migrate)

```ts
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({}); // reads GOOGLE_API_KEY from env
// or explicitly: new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY })

const response = await ai.models.generateContent({
  model: "gemini-2.5-flash",
  contents: "Tell me a story in 300 words.",
});
console.log(response.text);
```
[[source]](https://ai.google.dev/gemini-api/docs/migrate)

Node-only env var note: the SDK's own README says to set `GOOGLE_API_KEY` (not `GEMINI_API_KEY`) for env-var auto-detection in Node. [[source]](https://www.npmjs.com/package/@google/genai) — to be safe, set **both** vars to the same value in Node projects.

### 2.3 Plain REST (curl) — no SDK
Classic `generateContent`:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Explain how AI works"}]}]}'
```
[[source: header pattern]](https://ai.google.dev/gemini-api/docs/batch-mode)

New Interactions endpoint:
```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/interactions" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.7-flash",
    "input": "Explain how AI works",
    "generation_config": { "temperature": 1.0 }
  }'
```
[[source]](https://ai.google.dev/gemini-api/docs/text-generation)

---

## 3. Free tier vs paid tier

### 3.1 How limits are measured
Three dimensions, evaluated independently — hitting **any one** triggers a rate-limit error even if the others are fine:
- **RPM** — requests per minute
- **TPM** — input tokens per minute
- **RPD** — requests per day (resets at **midnight Pacific time**, not UK time)

Limits are per **Google Cloud project**, not per API key, and are tighter for experimental/preview models. [[source]](https://ai.google.dev/gemini-api/docs/rate-limits)

### 3.2 The actual numbers — read this caveat first
Google renders the exact free-tier/Tier-1/Tier-2/Tier-3 RPM/TPM/RPD numbers as an interactive, per-model table on the [rate-limits page](https://ai.google.dev/gemini-api/docs/rate-limits) that requires JavaScript — our automated fetch of that page could only retrieve the surrounding prose, not the live numbers, and third-party trackers disagree with each other on exact figures (e.g. reported free-tier RPD for `gemini-2.5-pro` ranges from 25 to 100 depending on the source, checked Aug 2026). **Treat every number below as directionally right but UNVERIFIED at the exact digit — before you rely on a number, open [aistudio.google.com/usage](https://aistudio.google.com/usage) or the live rate-limits page for your own project.**

Rough shape reported by multiple independent trackers (cross-referenced, not primary-sourced): [[aggregator 1]](https://www.aifreeapi.com/en/posts/gemini-api-free-tier-rate-limits) [[aggregator 2]](https://tokenmix.ai/blog/gemini-api-free-tier-limits) [[aggregator 3]](https://aipromptshub.co/blog/gemini-api-free-tier-rate-limits)

| Model class | Free tier RPM | Free tier TPM | Free tier RPD |
|---|---|---|---|
| Flash / Flash-Lite | ~10–15 | ~250K–1M | ~250–1,500 |
| Pro (2.5 Pro) | ~5 | ~250K | ~25–100 |

Paid Tier 1 jumps roughly 20–200x on RPM and removes the RPD cap entirely on Flash models, per the same trackers.

### 3.3 What's actually verified: the tier ladder and spend caps
This part **is** confirmed directly from Google's own docs and is consistent across the rate-limits and billing pages:

| Usage tier | How you qualify | Monthly billing-account spend cap |
|---|---|---|
| **Free** | Active project or free trial (no billing account) | N/A |
| **Tier 1** | Link an active Cloud Billing account | $250 |
| **Tier 2** | $100 cumulative spend + 3 days since first successful payment | $2,000 |
| **Tier 3** | $1,000 cumulative spend + 30 days since first payment | $20,000–$100,000+ |

[[source]](https://ai.google.dev/gemini-api/docs/rate-limits) [[source]](https://ai.google.dev/gemini-api/docs/billing)

Separately, there's a **spend-based rate limit** (a rolling 10-minute window, independent of RPM/TPM) that also throws `429 RESOURCE_EXHAUSTED` if you burst too much spend at once:

| Tier | Spend limit per 10 minutes |
|---|---|
| Free | N/A |
| Tier 1 | $10 |
| Tier 2 | $50 |
| Tier 3 | $200 |

[[source]](https://ai.google.dev/gemini-api/docs/rate-limits)

Tier upgrades are **automatic** once you meet the qualification (no form to fill for Tier 1→3); the monthly cap is enforced at the **billing account** level across all linked projects — hit it and every project on that billing account pauses until the 1st of next month. [[source]](https://ai.google.dev/gemini-api/docs/billing)

### 3.4 Training data — and a real legal gotcha for a UK event
- **Free tier:** your prompts/outputs **are** used to improve Google's products. **Paid tier:** they are **not**. This is stated per-model on the pricing page (every model row has a "Used to improve our products: Yes/No" line). [[source]](https://ai.google.dev/gemini-api/docs/pricing) — if your demo uses any real/sensitive data, use the paid tier (min $10 prepay, see §1.1) or synthetic data instead.
- **Bigger one:** Google's Additional Terms of Service state *"You may use only Paid Services when making API Clients available to users in the European Economic Area, Switzerland, or the United Kingdom."* [[source]](https://ai.google.dev/gemini-api/terms) — read literally, if your hackathon build will be used by anyone else physically in the UK (not just you testing it), the **free tier is not a compliant option** for that usage. For a same-day demo to judges this is unlikely to be enforced/checked, but if you plan to actually ship or publicly demo the thing to a UK audience beyond the judging panel, budget the $10 minimum paid-tier prepay now.

---

## 4. Cost control

### 4.1 Context caching (do this for free, it's automatic)
**Implicit caching** is on by default for Gemini 2.5+ models — no code changes, Google auto-detects repeated prefixes and discounts you. Minimum prompt size to be cache-eligible: [[source]](https://ai.google.dev/gemini-api/docs/caching)

| Model | Minimum tokens for implicit cache |
|---|---|
| Gemini 3.7 / 3.6 / 3.5 Flash, 3.1 Pro Preview | 4,096 |
| Gemini 2.5 Flash / Pro | 2,048 |

Tips to actually hit the cache: put your large, repeated content (system prompt, long context doc) **first** in the prompt, and fire similar requests close together in time. Check `usage.total_cached_tokens` in the response to see if you hit it. [[source]](https://ai.google.dev/gemini-api/docs/caching)

**Explicit caching** (`client.caches.create/get/list/update`, with a configurable `ttl`) is for when you want to pin a large context (e.g. a big system prompt or document) across many calls and control exactly when it expires — you pay a lower per-token rate for cached tokens plus an hourly storage fee (see pricing table in §4.4). [[source]](https://ai.google.dev/gemini-api/docs/generate-content/caching)

### 4.2 Batch API — 50% off, for stuff that isn't demo-critical
The Batch API runs at **50% of interactive cost**, target turnaround 24h (usually much faster), and supports context caching too. **Caveat: it currently only works with `generateContent`, not the new Interactions API.** Good for eval runs, pre-generating demo content, or bulk data prep — not for anything the judges will watch happen live. [[source]](https://ai.google.dev/gemini-api/docs/batch-mode)

### 4.3 Thinking budget — the easiest lever to cut cost/latency
- **Gemini 2.5 models** use `thinkingBudget` — a raw token count. Dynamic thinking is on by default; **set `thinkingBudget: 0` to disable thinking entirely** on eligible models, which is often the single biggest latency/cost win for simple tasks.
- **Gemini 3.x models** use `thinkingLevel` instead — a string: `minimal` / `low` / `medium` / `high`. Gemini 3.7 Flash defaults to `medium`; Live API audio models default to `minimal` for lowest latency.
[[source]](https://ai.google.dev/gemini-api/docs/live-api/capabilities) [[source]](https://ai.google.dev/gemini-api/docs/latest-model)

Output pricing includes thinking tokens, so an unbounded `thinkingBudget`/high `thinkingLevel` on a model you're calling hundreds of times is where hackathon bills quietly balloon — turn it down for anything that doesn't need deep reasoning.

### 4.4 Token counting — check before you burn budget
```python
count = client.models.count_tokens(model="gemini-2.5-flash", contents=[...])
print(count.total_tokens)
```
Also available in JS as `client.models.countTokens(...)`, and the newer Interactions API reports `interaction.usage.total_input_tokens` directly on the response — no separate call needed if you're already using `interactions.create`. [[source]](https://ai.google.dev/gemini-api/docs/tokens)

### 4.5 Pricing reference (per 1M tokens, USD) — verified from the official pricing page
[[source: full table]](https://ai.google.dev/gemini-api/docs/pricing)

| Model | Free tier | Paid input | Paid output (incl. thinking) | Cached input | Cache storage/hr |
|---|---|---|---|---|---|
| Gemini 2.5 Flash-Lite | Free | $0.10 | $0.40 | $0.01 | $1.00 |
| Gemini 2.5 Flash | Free | $0.30 | $2.50 | $0.03 | $1.00 |
| Gemini 2.5 Pro (≤200k ctx) | Free | $1.25 | $10.00 | $0.125 | $4.50 |
| Gemini 2.5 Pro (>200k ctx) | Free | $2.50 | $15.00 | $0.25 | $4.50 |
| Gemini 3.7 Flash (through 31 Dec 2026) | Free | $0.75 | $3.75 | $0.075 | $0.50 |
| Gemini 3.7 Flash (from 1 Jan 2027) | Free | $1.50 | $7.50 | $0.15 | $1.00 |

Note: Gemini 3.7 Flash also has a cheaper **"Flex"** processing tier ($0.375 in / $1.875 out through end of 2026) for latency-tolerant workloads, separate from Batch API. [[source]](https://ai.google.dev/gemini-api/docs/pricing)

### 4.6 "What does a hackathon day cost?" — worked estimate
Assume a busy day: **500 API calls**, averaging 2,000 input tokens + 500 output tokens each (a realistic agent-with-context workload), all on the **paid tier** (so nothing above is capped by free-tier RPD):

- **On `gemini-2.5-flash`:** 1M input tokens × $0.30 + 250K output tokens × $2.50/1M = **$0.30 + $0.63 ≈ $0.93 for the day**
- **On `gemini-2.5-pro` (≤200k ctx):** 1M input × $1.25 + 250K output × $10/1M = **$1.25 + $2.50 ≈ $3.75 for the day**

*(This is a derived estimate from the verified per-token prices above × an assumed call volume — not an official Google figure. Your actual usage will very likely stay entirely inside the free tier unless you're hammering it much harder than this.)* Realistically: **most hackathon teams will spend $0**, because the free tier's RPD easily covers iterative dev + a live demo, and the $10 minimum paid-tier prepay (if you need it for the EU/UK-user reason in §3.4, or to remove RPD caps) buys far more headroom than a single day needs.

---

## 5. AI Studio vs Vertex AI (now "Gemini Enterprise Agent Platform")

**Naming note (flagging explicitly, verify if it matters to you):** Google's own current SDK docs (both the `@google/genai` npm README and the `google-genai` Python README, fetched today) refer to the enterprise/Cloud surface as **"Gemini Enterprise Agent Platform"**, not "Vertex AI" — this appears to be a 2026 rebrand. Some still-current docs (Gemini CLI) use the older "Vertex AI" name and `GOOGLE_GENAI_USE_VERTEXAI` env var. Both naming conventions appear live in different docs right now; if you go down this path, re-check which one your exact SDK version expects. [[source 1]](https://www.npmjs.com/package/@google/genai) [[source 2]](https://github.com/googleapis/python-genai)

**For today, use AI Studio (the Gemini Developer API — everything in §1–§4 above).** It's what `GEMINI_API_KEY`/`GOOGLE_API_KEY` talk to, it's zero-setup, and it's what almost every hackathon tutorial assumes.

**Reach for Vertex AI / Gemini Enterprise Agent Platform instead if:** you need enterprise IAM/VPC-SC controls, guaranteed no-training-on-data even on cheaper tiers, or you're already sitting on Google Cloud credits (Vertex AI usage is what those credits actually pay for — see §6). It also has an **Express Mode**: no billing account needed for the first 90 days, account-specific quotas. [[source]](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview)

Switching the SDK client (per the currently-documented Node env vars):
```bash
# Gemini Developer API (default — what this whole doc assumes)
export GOOGLE_API_KEY="your-api-key"

# Gemini Enterprise Agent Platform / Vertex AI
export GOOGLE_GENAI_USE_ENTERPRISE=true   # some docs: GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
```
```ts
const ai = new GoogleGenAI(); // picks up whichever env vars are set
```
[[source]](https://www.npmjs.com/package/@google/genai)

Unless you already have a specific enterprise/compliance reason, **don't switch today** — it adds GCP project/IAM setup overhead you don't need in a 5-hour hackathon.

---

## 6. Credits — what can actually help you today vs. later

| Option | Amount | Usable today? | Source |
|---|---|---|---|
| **Ask the organisers** | Unknown, likely an event key/quota bump | **Yes — do this first** | Recommendation, not sourced |
| Gemini API free tier | Ongoing, no card, no expiry | **Yes — you already have it** | [aifreeapi.com](https://www.aifreeapi.com/en/posts/google-gemini-api-free-tier) (permanent-free-tier claim, cross-check against §3) |
| Google Cloud $300 new-account credit | $300, 90 days | Maybe — reportedly **cannot** be spent on the Gemini API inside AI Studio, only broader Cloud/Vertex usage (UNVERIFIED, third-party claim, not confirmed on an official page) | [tahoor.beehiiv.com](https://tahoor.beehiiv.com/p/google-cloud-300-credit-vertex-ai-rebrand-2026), [Google Cloud Free Program](https://docs.cloud.google.com/free/docs/free-cloud-features) |
| Vertex AI Express Mode | Account-specific quota, 90 days, no billing | Yes if you switch to Vertex (see §5) | [Google Cloud docs](https://cloud.google.com/vertex-ai/generative-ai/docs/start/express-mode/overview) |
| Google for Startups Cloud Program | Up to $200K ($350K AI-track) | **No** — application/review process takes days, not usable mid-hackathon; relevant only if you continue the project afterward | [cloud.google.com/startup](https://cloud.google.com/startup) |
| MLH Gemini partnership perks | ~$10/mo student credit, $300 new-account | Only if this event is MLH-affiliated — **UK AI Agent Lab isn't confirmed as an MLH event**, don't assume it applies | [mlh.com/partners/gemini](https://www.mlh.com/partners/gemini) |
| Kaggle/Colab Secrets | No extra quota — just a safe place to store *your own* key | Yes, if you're prototyping in a notebook | [Kaggle: configuring secrets](https://www.kaggle.com/code/satyaprakashswain/configuring-gemini-api-key-in-kaggle) |

**Bottom line for a 5-hour hackathon: the free tier + a $10 paid-tier top-up (if you hit a wall) is the realistic path.** Everything else in this table is either not usable within the time box or unconfirmed for this specific event.

---

## 7. Troubleshooting table

| Error / symptom | Cause | Fix |
|---|---|---|
| `429 RESOURCE_EXHAUSTED` | Exceeded RPM/TPM/RPD, **or** hit the spend-based 10-min cap (§3.3) | Wait + retry with backoff; shrink context/output size; if it's a project you're actively spending on, [request a rate-limit increase](https://ai.google.dev/gemini-api/docs/rate-limits#request-rate-limit-increase); or enable billing to move off Free tier |
| `400` "API key not valid" | Key mistyped/revoked, wrong env var read, or key is IP/referrer-restricted away from your current network | Re-check `aistudio.google.com/api-keys` — is the key active? Confirm `echo $GEMINI_API_KEY` prints it; remember `GOOGLE_API_KEY` overrides `GEMINI_API_KEY` if both are set |
| Empty `candidates`, response looks blank | Safety filter blocked the prompt or output at your configured threshold | Inspect `response.candidates[0].finishReason` and `.safetyRatings`; loosen the relevant category's `safetySettings` threshold (e.g. `BLOCK_ONLY_HIGH`) if appropriate for your use case |
| `finishReason: MAX_TOKENS`, truncated/empty text | `maxOutputTokens` too low — thinking tokens count against this budget on reasoning models | Raise `maxOutputTokens`, or lower/zero out `thinkingBudget` / drop `thinkingLevel` (§4.3) so more of the budget goes to the visible answer |
| Region-restriction / "not available in your region" landing page | Your account/network isn't in a [supported country](https://ai.google.dev/gemini-api/docs/available-regions), or the Google Account's age (18+) isn't verified | Check the supported-regions list (UK is on it); verify age on your Google Account |
| Blocked when serving to real UK/EU/CH users | ToS restriction (§3.4): free tier can't be used to serve EEA/Switzerland/UK end users | Enable billing / paid tier before shipping to anyone in those regions |
| CORS error / network request fails calling the API straight from browser JS | You're calling `generativelanguage.googleapis.com` directly from client-side code — this is a security anti-pattern Google explicitly warns against, not a bug to route around | Put a thin backend proxy in front that holds the key server-side; never ship the raw key to the browser |
| Live API session won't connect / model unavailable | Live API (voice/streaming) preview models can have narrower regional/model availability than the standard text API — **exact list UNVERIFIED**, we couldn't confirm a specific UK carve-out | Test the `ai.live.connect()` call early, don't assume parity with the text API; have a non-Live fallback path for the demo |

Sources for this section: [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), [migrate guide / safety settings example](https://ai.google.dev/gemini-api/docs/migrate), [available regions](https://ai.google.dev/gemini-api/docs/available-regions), [ToS](https://ai.google.dev/gemini-api/terms), [npm CAUTION on client-side keys](https://www.npmjs.com/package/@google/genai), [Live API capabilities](https://ai.google.dev/gemini-api/docs/live-api/capabilities).

---

## 8. Copy-paste starter files

**`.env.example`**
```
GEMINI_API_KEY=your_api_key_here
GOOGLE_API_KEY=your_api_key_here
```
*(Set both to the same value — see §1.2/§2.2 on which SDK reads which var.)*

**`requirements.txt`**
```
google-genai
```
*(Unpinned deliberately — this SDK ships fast; pin a version once your demo is stable if you want reproducibility.)* [[source]](https://ai.google.dev/gemini-api/docs/migrate)

**`package.json`** (dependencies snippet)
```json
{
  "dependencies": {
    "@google/genai": "latest"
  }
}
```
[[source]](https://ai.google.dev/gemini-api/docs/migrate)

---

*Compiled 22 Aug 2026 from ai.google.dev/gemini-api/docs (api-key, quickstart, rate-limits, pricing, billing, caching, batch-mode, thinking, tokens, migrate, migrate-to-interactions, terms, available-regions, live-api/capabilities), the `@google/genai` npm page, the `google-genai` GitHub repo, Google Cloud's Vertex AI Express Mode docs, and cross-referenced third-party trackers for the items explicitly marked UNVERIFIED above. Where Google's own rate-limit numbers are JS-rendered and couldn't be scraped, this doc says so rather than guessing.*
