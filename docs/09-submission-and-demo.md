# Submission & Demo Pack — UK AI Agent Lab 22 Aug 2026

**DEADLINE: 17:30 TODAY** | Winners announced Monday 24 August | Top 3–5 live demo round likely

---

## DEADLINE-ORDERED CHECKLIST

**WHY submit a draft early:** On Devpost/submission platforms, submissions can be incomplete but visible to judges from the moment you create them. Submitting at 15:00 (2.5 hours early) means:
- If the platform crashes at 17:00, you're already in the queue
- Judges can start reviewing immediately after your live pitch
- Network hiccups won't cost you the deadline
- You have 2.5 hours to fix a missing video or typo without panic

---

### **HOUR ZERO: 13:00–13:30 (Right after briefing)**

- [ ] **Confirm the submission platform** — what URL, what fields are required
- [ ] **Create a GitHub repo public** (if not already) — judges will check this first
- [ ] **Create the draft submission** — go to the platform, fill Title + Tagline, **submit as DRAFT** even if empty
  - **Proof point:** You have a submission ID, judges see your project name, platform backups are triggered
- [ ] **Screenshot the submission URL** — send to team chat (proof it exists before 17:30)

---

### **13:30–14:30: Write the submission fields**

- [ ] **Tagline** (12 words max) — copy from template below, adapt to your project
- [ ] **Problem statement** (30 seconds / ~70 words) — why this matters
- [ ] **Solution** (30 seconds / ~70 words) — what you built
- [ ] **Gemini/Gemma usage** (1 minute / ~150 words) — **single most important field for Google sponsorships** — be specific: which API, which features, how it's core to the solution
- [ ] **Tech stack** — list languages, frameworks, APIs (one line each)
- [ ] **What's next** (optional but recommended) — 1 sentence post-hackathon plan
- [ ] **Team members** — names and roles (be precise: "Alice (Lead / Gemini integration)" not just "Alice")

---

### **14:30–15:00: README & repo polish**

- [ ] **README.md in repo root** — copy template below
  - One sentence what it does
  - GIF/video demo slot (can be placeholder until video is ready)
  - Quickstart (install + run in 3 lines)
  - Architecture diagram (can be ASCII or link to docs/)
  - Which Gemini/Gemma features and in which files
  - Known limitations (honest, 2–3 lines — judges respect this more than overpromising)
- [ ] **.gitignore**: ensure no `.env`, `keys/`, secrets, node_modules
- [ ] **Commit everything** — `git add -A && git commit -m "hackathon submission v1"`
- [ ] **Check GitHub page loads** — repo is public, README renders, no broken images

---

### **15:00–15:30: Update submission with repo link + draft video placeholder**

- [ ] **Update submission fields** on the platform
  - Add GitHub repo URL
  - Add video link (use placeholder like "https://youtu.be/uploading…" for now)
  - **Do NOT submit yet** — keep as Draft
- [ ] **Double-check field lengths** — if platform has character limits, trim excess

---

### **15:30–16:45: Record demo video**

- [ ] **Set up recording environment** — quiet room, good lighting, close Slack/email
- [ ] **Do a dry run** — 90 seconds, click through the key moments
- [ ] **Record video** (see video guide below)
  - macOS: QuickTime Player (Cmd+Ctrl+Space, select area, record 2–3 min)
  - Audio test first (play a tone, record 5 sec, listen back)
  - Do 2 takes if first one has an "um" or freeze
- [ ] **Export as MP4** — 1080p, 30fps, <500 MB
- [ ] **Upload to YouTube (unlisted) or Loom**
  - Loom is faster (15–30 sec processing vs 5–15 min YouTube)
  - YouTube is more stable (won't get rate-limited, embed works everywhere)
  - **Upload by 16:30** to avoid processing delays near the deadline
- [ ] **Test the link** — open in incognito, video plays to end

---

### **16:45–17:00: Final submission**

- [ ] **Update video URL** on submission platform
- [ ] **Final proofread:**
  - No typos, no "TODO"s
  - All links clickable (repo, video, demo URL if live)
  - Team names spelled right
- [ ] **Click SUBMIT** (not Draft) by **17:10** — gives you a 20-minute buffer before hard deadline

---

### **17:10–17:30: Fallback protocol**

- [ ] **If video didn't upload:** link to a still screenshot of the demo + note "video processing, will be live by 18:00"
- [ ] **If submission platform crashes:** email the organizers the submission JSON / screenshot
- [ ] **If you have 2 minutes left:** add your email to the submission so judges can reach you

---

---

## SUBMISSION FIELD TEMPLATES

### **Tagline (One sentence, 12 words max)**

```
[Project Name]: [One-word problem] solution via [Gemini/Gemma feature].
```

**Examples:**
- "AgentAI: Real-time safety audits powered by Gemini's multimodal reasoning."
- "BuildBot: Autonomous code review agent using Gemma for latency-critical tasks."

**Your template:**
```
[Fill in]: __________ solution via __________.
```

---

### **Elevator Pitch (30 sec / ~70 words)**

```
[Target audience] struggles with [problem statement].

Existing tools [current gap]. 

We built [project name], which [core mechanism using Gemini/Gemma].

Result: [quantified win: faster / cheaper / more accurate].
```

**Example:**
```
DevOps teams waste 3+ hours per day triaging CI/CD failures.
Existing dashboards are reactive dashboards, not predictive.
We built BuildBot, an autonomous agent that watches your GitHub Actions and proposes fixes before the build breaks—powered by Gemini's code understanding.
Result: 60% fewer failed deployments.
```

**Your template:**
```
[Target audience] struggles with [problem].

Existing tools [gap]. 

We built [name], which [mechanism].

Result: [win].
```

---

### **Problem (1 min / ~150 words, or omit if covered in Pitch)**

```
[Industry] teams spend [time/money] on [task].

The cost: [business impact — slower shipping, security risk, burnout, etc.].

Why it matters: [why existing solutions don't work, not just "there's no tool"].
```

---

### **Solution (1 min / ~150 words)**

```
We built [name], which:

1. [What it does] — [how user sees it: CLI/web/API].
2. [What it understands] — [what data inputs it takes].
3. [What it decides] — [what actions it takes or recommends].

Core tech: [Your stack — no jargon yet].

Why it works: [Specific property that Gemini/Gemma enables — speed, reasoning, multimodal, context window, etc.].
```

---

### **How We Used Gemini/Gemma** ⭐ *CRITICAL FIELD*

**This field carries the most sponsor weight.** Be specific: list the exact API call, which feature, why that feature was essential (not "we used Gemini" — "we used Gemini's function calling to parse ambiguous error logs in <200ms").

```
**Model:** [gemini-2.0-flash / gemma-2-27b-it / etc.]

**Feature 1: [Name]**
- What it does: [Plain English]
- Why we used it: [Problem it solved for us]
- Code location: [file.py:line or src/api/routes.ts:42]
- Example: [One-line sample prompt or use case]

**Feature 2: [Name]**
- What it does:
- Why we used it:
- Code location:
- Example:

**Performance:** [If relevant — latency, cost, accuracy vs alternative]

**Why Gemini/Gemma was irreplaceable:** [What would break if you removed it? Not "code wouldn't run" but "we'd lose real-time reasoning" or "cost would triple"]
```

**Example (Good):**
```
**Model:** Gemini 2.0 Flash via Google AI API

**Feature 1: Multimodal understanding (vision + text)**
- What it does: Accepts screenshots, PDFs, and log text in one request
- Why we used it: Users paste screenshot + description; Gemini extracts both and correlates them with logs
- Code location: src/api/analyze.ts:142–156 (calls gemini.generateContent with vision parts)
- Example: User uploads ERR_HEAP_OUT_OF_MEMORY screenshot → Gemini identifies the memory leak pattern

**Feature 2: Structured output (function calling)**
- What it does: Returns JSON in a guaranteed schema
- Why we used it: We pipe the output to a database; JSON schema validation is automatic
- Code location: src/agents/fixer.py:89 (schema parameter in tool_config)
- Example: `{"type": "MEMORY_LEAK", "file": "worker.js:34", "action": "PROFILE"}`

**Performance:** 450ms avg latency (sub-second for real-time UX), $0.12/1K input tokens (unit economics hold at scale)

**Why Gemini was irreplaceable:** Without multimodal input, we'd need two separate APIs (OCR + LLM), adding 800ms latency and loss of cross-modal context. Without structured output, we'd do regex parsing on 18 different error patterns — fragile and unmaintainable.
```

---

### **Tech Stack**

```
- **Language:** [Python / TypeScript / Go / etc.]
- **Frontend:** [React / Vue / None / etc.]
- **Backend:** [FastAPI / Express / Django / None / etc.]
- **AI:** Gemini 2.0 Flash (or Gemma 2 27B)
- **Database:** [PostgreSQL / Supabase / Redis / None]
- **Deployment:** [GitHub Pages / Vercel / Railway / Local demo]
- **External APIs:** [List non-Gemini APIs used — optional]
```

---

### **What's Next (optional, 1 sentence)**

```
Post-hackathon: [Deploy to X, add Y feature, or open-source the codebase].
```

**Examples:**
- "Post-hackathon: Open-source on GitHub and add real-time alerting."
- "Post-hackathon: Deploy to Vercel and integrate with Slack for team notifications."

---

### **Team**

```
- [Name] — [Role: Lead / Fullstack / AI / DevOps / Product]
- [Name] — [Role]
```

**Be specific.** "Alice (Lead / Gemini integration)" > "Alice". Helps judges remember who did what if you advance to the demo round.

---

---

## README TEMPLATE

```markdown
# [Project Name]

[One sentence: what it does in plain English]

## What It Does

[1–2 sentences. No jargon. Answer: "Why should I use this instead of X?"]

## Demo

![Demo GIF or video thumbnail](docs/demo.gif)
[Or] → [Watch 2-min demo](https://www.youtube.com/watch?v=...)

## Quickstart

### Install
\`\`\`bash
git clone [repo]
cd [repo]
pip install -r requirements.txt  # or: npm install
\`\`\`

### Run
\`\`\`bash
python main.py  # or: npm start
# Output: [what the user sees — e.g., "Server running on http://localhost:3000"]
\`\`\`

### Try It
\`\`\`bash
# [One concrete example the user can copy-paste]
python main.py --input "ERR_HEAP_OUT_OF_MEMORY"
# Output: Suggested fix + code location
\`\`\`

## How It Uses Gemini/Gemma

| Feature | Where | Why |
|---------|-------|-----|
| [Multimodal vision] | `src/api/analyze.py:42–56` | Parse screenshots + text in one request |
| [Structured output] | `src/agents/fixer.ts:89` | Return JSON for database insertion |
| [Long context] | `src/chunker.py:12` | Handle 50KB logs in one prompt |

See [API docs](docs/gemini-usage.md) for full details and example prompts.

## Architecture

```
[User Input]
    ↓
[Gemini API] → [Structured Output] → [Action / Recommendation]
    ↓
[Logs / Screenshots]
```

## Tech Stack

- **AI:** Gemini 2.0 Flash
- **Backend:** [Framework]
- **Frontend:** [Framework or "CLI"]
- **Deployment:** [Where it runs]

## Known Limitations

- [Limitation 1: honest description]
- [Limitation 2: impact + workaround if any]
- [Limitation 3]

## What's Next

- [ ] Add real-time alerting
- [ ] Deploy to production
- [ ] Support additional error types

## License

[MIT / Apache 2.0 / etc.]

---

**Built at UK AI Agent Lab, 22 August 2026.**
```

---

---

## DEMO VIDEO GUIDE

**Length:** 2–3 minutes (not more; judges see 100+ videos)

**Structure:**
- **0–5 sec:** Show the problem (screenshot of error log, user's pain point)
- **5–30 sec:** Live demo of your solution (click, type, show output)
- **30–45 sec:** Explain what just happened (why it works, what tech made it possible)
- **45–60 sec:** Show the code for 5 seconds (Gemini prompt, key function, integration point) — optional but impressive
- **60–120 sec:** Next steps or "why this matters" — optional

**Recording on macOS:**

### Option 1: QuickTime Player (Built-in, Free)
1. Open QuickTime Player (Cmd+Space, type "QuickTime")
2. File → New Screen Recording
3. Click ⏹ button to start
4. Click the ⏹ button in menu bar to stop
5. File → Save
6. Keep video <500 MB (trim if needed: open in iMovie, export as MP4)

### Option 2: ScreenFlow (Paid, $99 — faster encoding)
1. Open ScreenFlow
2. Click "Record"
3. Select screen area + microphone
4. Click "Stop"
5. Export as MP4 (H.264, 1080p, 30fps)

### Option 3: Free alternatives
- **Loom** (web browser, sign up free): record directly in browser, auto-uploads
- **OBS** (open-source): steeper learning curve, best quality
- **Cmd+Shift+5** (built-in): screen recording + screenshot tool (macOS 10.14+)

**Audio tips (critical — no dropouts):**
- Use a quiet room (close Slack, email, mute notifications)
- Use headphones to monitor during recording
- Speak clearly at 1.0x speed — not too fast
- Do a **30-second audio test** before the full recording: record 30 sec of speaking, play it back, check volume and clarity
- If audio drops, **re-record that section** — don't try to fix in post
- Use a USB headset mic if your Mac's built-in mic sounds robotic

**Video upload:**
- **Loom (faster, recommended for tight deadline):**
  - Go to loom.com, sign up free, click "Start recording"
  - Browser extension auto-uploads when you finish
  - Shareable link ready in 30 seconds
  - **Risk:** Loom can be slow on deadline day; upload by 16:30
  
- **YouTube (more stable for embedding):**
  - Go to youtube.com, click "Create" → "Upload video"
  - Select "Unlisted" (not Private — judges need to view without signing in)
  - Title: "[Project Name] — UK AI Agent Lab Demo"
  - Upload by 16:30; YouTube takes 5–15 min to process depending on server load
  - **Common trap:** "Processing" status can last 30+ min near the deadline if servers are busy
  - **Mitigation:** Upload early, use Loom if YouTube stalls

**Submission:**
- Test the link in incognito mode before submitting (confirm it plays)
- Paste the link into the submission platform by 17:00

---

---

## LIVE DEMO RUN-SHEET (For Top 3–5 Round)

**Format:** ~2 minutes on stage, judges ask follow-ups

**Who says what:**

```
[00:00–00:10] LEAD: "Hi, I'm [Name]. Today we're solving [problem]."

[00:10–00:30] LEAD: "Here's the problem: [show 1 screenshot or tell a story]."

[00:30–01:15] TECH LEAD: "We built [name]. Let me show you." 
[Walk through live demo, click once, explain output]
[Click one more time, show different scenario]

[01:15–01:40] TECH LEAD: "Under the hood, we're using Gemini's [feature] 
to [what it enables]. This lets us [business impact: faster/cheaper/more accurate]."

[01:40–01:50] LEAD or TECH LEAD: "Code's on GitHub. Thanks."

[01:50–02:00] [Silence — judges ask questions]
```

**What to have open (in browser tabs):**
1. **Live demo app** (localhost:3000 or production URL) — tab 1, ready to click
2. **GitHub repo** — tab 2, show README and key file (Gemini integration point)
3. **Video as fallback** — tab 3, YouTube unlisted link (if live demo dies, play video instead)

**If the network dies during your live demo:**
- Pause, smile, say "Network hiccup—let me show you the video instead"
- Click to tab 3, play the 2-min video
- Judges still see the full demo; you lose ~20 seconds but don't lose the demo

**Never type code on stage.** If you must show code:
- Pre-open the file and point to it (don't type)
- Read one function signature from the screen aloud
- Judges want to see the demo run, not your typing speed

**Dress code:** Casual is fine (this is a hackathon), but one person should look presentable (dark shirt, no wrinkles). You're not being judged on clothes; professionalism matters.

**Energy:** Speak at normal pace, pause for a breath between sentences. Smile. A 2-minute pitch with awkward silence is better than rushing through 3 minutes. Judges can always ask for more details.

---

---

## JUDGE Q&A PREP SHEET

**Judges typically ask these 8 questions. Prepare 1-paragraph answers.**

### 1. "What's the core innovation here?"

**What they want:** Why your idea is novel / harder than it sounds.

**One-paragraph answer template:**
```
The innovation is [specific property of your approach]. Most solutions do [common approach], 
which fails because [limitation]. We solved it by [your specific method], which lets us 
[competitive advantage: speed / cost / accuracy / new capability]. This works because 
[why Gemini/Gemma was essential — not just "we used AI"].
```

**Example:**
```
The innovation is real-time root-cause analysis of production errors. Most tools grep logs 
and show dashboards. They fail because humans spend 3 hours correlating error patterns across 
20 different log files. We solved it by sending screenshots + raw logs to Gemini in parallel, 
which extracts context from both modalities and proposes a fix in 400ms. This works because 
Gemini's multimodal understanding means we don't need separate OCR and NLP pipelines.
```

---

### 2. "How do you know this actually works? Do you have metrics?"

**What they want:** Evidence, not promises. Numbers beat "it feels fast."

**One-paragraph answer template:**
```
We tested on [dataset / scenario]. [Metric 1] improved by [%]. [Metric 2] is [number]. 
For example, [1 concrete story — "we ran this on 50 real error logs and got 92% accuracy"]. 
The main limitation is [honest constraint — "we haven't tested on custom error formats yet"].
```

**Example:**
```
We tested on 50 real GitHub Actions failures from [well-known repo]. Our agent found 
the root cause in 89% of cases (vs 40% for pattern matching). Average time-to-fix was 
3 minutes (vs 45 minutes manually). We also dogfooded it on our own CI—caught a memory 
leak we missed. The main limitation is we haven't tested on Kubernetes / Docker Compose 
error logs yet.
```

---

### 3. "Why Gemini specifically? Could you do this with [cheaper LLM]?"

**What they want:** You understand the trade-offs. If you say "yes, but," that's fine—shows maturity.

**One-paragraph answer template:**
```
We chose Gemini because [specific feature we need]. We tested [cheaper alternative] 
and found [concrete difference — latency / accuracy / cost]. For example, [1 benchmark]. 
If cost became critical, we could [fallback plan], but it would [trade-off]. 
For the use case we're solving, [why Gemini is the right call].
```

**Example:**
```
We chose Gemini 2.0 Flash because of sub-500ms latency for multimodal input. We tested 
Claude 3 Haiku and saw 2.3-second latency (too slow for our real-time UX). We also tested 
Llama 3.1 locally on a GPU and got 70% accuracy on error classification vs Gemini's 92%. 
If we hit cost limits, we'd add a classifier layer (cheaper LLM) as a filter, but Gemini's 
reasoning is essential for novel error patterns. For our user base, the sub-second latency 
is a product differentiator.
```

---

### 4. "Who is your user? Would they actually pay for this?"

**What they want:** Your business model. "Anyone could use it" is not an answer.

**One-paragraph answer template:**
```
Our user is [specific persona — e.g., "DevOps engineers at 50+ person startups"]. 
They spend [time/money] on [problem]. We'd charge [pricing model — per-API-call / per-month / per-user]. 
At [scale], that's [$monthly ARR]. We know this because [customer signal — calls with beta users / competitor pricing / market research].
```

**Example:**
```
Our user is DevOps / SRE teams at 50+ person startups. They spend ~3 hours per day 
diagnosing CI/CD failures (at $150/hour loaded, that's $450/day = $100K/year in engineering time). 
We'd charge $500/month per team, which is a 5x ROI for a team of 4 engineers. We validated 
this by talking to 8 startup CTOs who said they'd pay up to $2K/month; competitor Datadog 
charges $10K+. Our moat is speed (response time < 1 min vs Datadog's 5+ min of human triage).
```

---

### 5. "What's your biggest risk or limitation?"

**What they want:** Honesty. Judges respect acknowledging a problem you haven't solved.

**One-paragraph answer template:**
```
Our biggest risk is [real constraint]. This could happen if [scenario]. We mitigate it by [safeguard]. 
If it became a blocker, we'd [pivot]. We're not worried about [common misconception] because [why].
```

**Example:**
```
Our biggest risk is hallucinations in error diagnosis. If Gemini generates a plausible-sounding 
but incorrect fix, a junior engineer might ship it. We mitigate by requiring human review before 
deployment; the agent generates 3 candidate fixes with confidence scores. If hallucinations became 
worse than human baseline, we'd add a fallback: local pattern matching for known error types. 
We're not worried about latency regression because Gemini's 2.0 Flash is consistently sub-500ms.
```

---

### 6. "How does this integrate with existing tools? (Datadog, Sentry, GitHub, Slack, etc.)"

**What they want:** Practical path to deployment. "It runs standalone" is a weakness in enterprise.

**One-paragraph answer template:**
```
We integrate via [API / webhook / CLI / plugin]. For example, [1 concrete integration]. 
It works with [3–5 popular tools]. We prioritized [most common tool] because [user research]. 
Next, we'd add [other tools] via [method — Zapier / custom integration / open-source SDK].
```

**Example:**
```
We integrate via GitHub Actions webhook + Slack API. When a CI job fails, we POST the logs 
to our agent, which responds with a Slack message containing the fix + code location. This 
works with any GitHub + Slack setup (90% of our target market). We prioritized GitHub because 
it's the source of truth for most teams. Next, we'd add Datadog log export via their API and 
PagerDuty incident creation for on-call escalation.
```

---

### 7. "What's your timeline? When would this be production-ready?"

**What they want:** Realistic shipping timeline. "3 months" is fine if you're honest.

**One-paragraph answer template:**
```
Timeline: [4 weeks / 3 months / etc.] to [milestone — "MVP ready for paid beta" / "5-company pilot"]. 
Blockers: [real dependency — "waiting for GitHub to approve our app" / "need payment processor integration"]. 
By [date], we want [concrete goal — "10 teams in beta" / "deploy to production"].
```

**Example:**
```
Timeline: 4 weeks to paid beta (6 teams). 8 weeks to GA (50+ teams). Blockers: We're waiting 
on GitHub to approve our app to the marketplace (typical 2–3 week SLA). By September, we want 
to deploy to production and hit $10K MRR. By Q4, we want to raise a seed round (already have 
3 LOIs from VCs).
```

---

### 8. "Why should we care? What's the impact?"

**What they want:** The "why this matters" answer. Connect to business, security, or developer joy.

**One-paragraph answer template:**
```
Impact: [1 stat]. This matters because [business / security / human benefit]. For [segment], 
this means [concrete outcome — "ship features faster" / "reduce MTTR by 10x" / "stop 
burnout"]. At scale, [long-term vision or societal impact if applicable].
```

**Example:**
```
Impact: Teams save 3+ hours per day on incident response. This matters because developer 
burnout is the #1 reason engineers leave startups. For DevOps teams, this means they can 
spend time on automation instead of firefighting. At scale, we're reducing the cognitive 
load of production support across thousands of teams—making engineering more joyful and less 
reactive.
```

---

---

## LAST 30 MINUTES: PANIC PROTOCOL

**17:00 — 17:10: Triage**

- [ ] Video uploaded? → Go to **5-min panic**
- [ ] Video still processing? → Go to **upload fallback**
- [ ] Submission platform down? → Go to **email backup**
- [ ] Typo in submission? → Too late, submit as-is

---

### **5-Min Panic: Video Never Uploaded**

**What to do:**
1. Screenshot your working app running locally (Cmd+Shift+4)
2. Open the submission, paste the screenshot URL
3. Add note: "Video processing; will upload by 18:00"
4. Judges see the screenshot; video can arrive late
5. Upload the video later (as long as before judging window closes tomorrow)

**What NOT to do:** Delete the submission and start over. You lose your place in the queue.

---

### **Upload Fallback: Video Processing Slow**

**If Loom is stuck:**
- Switch to YouTube (File → Export as MP4, drag into YouTube)
- Wait max 5 minutes; if YouTube isn't processing by 17:05, give up and use screenshot fallback above

**If YouTube is stuck:**
- Paste a Loom link instead (can still process while you sleep, Loom emails you when ready)
- Add note: "Video available tomorrow morning"

---

### **Email Backup: Platform Down**

If the submission platform is unreachable at 17:15:

1. **Screenshot your draft submission** (proof you created it)
2. **Email the organizers** (address in briefing):
   - Subject: "UK AI Agent Lab Submission — [Team Name] — [Project]"
   - Body: "[Project name]. GitHub: [link]. Demo: [link]. Team: [names]."
   - Attach the screenshot
3. **Post in the team Slack channel** with the email receipt (proof you sent it)

The organizers will manually add you to the submission queue. You're in.

---

### **Last 30 Sec: Build Breaks at 17:00**

**Scenario:** You try to test the live demo and it crashes.

**What to do:**
1. **Kill the app.** Don't try to fix it live.
2. **Play the video instead** (you have it, right?).
3. **Smile and say:** "The server's restarting—let me show you the demo video instead."
4. **Judges still see the whole thing.** You lose 10 seconds and credibility; you don't fail.

**What NOT to do:**
- Try to code on stage
- Blame the network
- Say "it works on my machine"
- Skip the demo entirely

---

### **What You CAN Safely Fake:**

- **Live demo is broken?** → Play video instead (judges understand CI/CD fails)
- **Video didn't upload?** → Screenshot + "processing, uploading overnight"
- **Feature didn't make the deadline?** → Don't mention it (judges don't know what you planned)
- **Didn't test on [tool]?** → Say "we'd add [X] next" (future plans are fine)

### **What You MUST NOT Fake:**

- **Metric you don't have.** ("We tested on 10,000 samples" when you tested on 50 — judges ask follow-ups and catch you)
- **A feature that doesn't exist.** If you claim it in the submission, judges will ask you to demo it.
- **Gemini integration if you didn't use it.** ("We used Gemini's reasoning" when you just used an API call — judges see code at GitHub)
- **Customer validation you don't have.** ("5 companies signed LOIs" — they ask which ones)

**The rule:** Anything you might need to defend on stage, make sure it's true.

---

---

## FINAL CHECKLIST — PRINT THIS AND CHECK OFF

- [ ] Draft submission created by **15:00**
- [ ] GitHub repo public by **15:30**
- [ ] README.md complete by **15:30**
- [ ] Video uploaded and tested by **16:45**
- [ ] Submission link works and loads by **16:50**
- [ ] Video link is live and plays end-to-end by **16:50**
- [ ] Team member names spelled correctly in submission by **17:00**
- [ ] Submission SUBMITTED (not Draft) by **17:10**
- [ ] Team screenshot of confirmation page posted to Slack by **17:15**

---

## SOURCES & CONFIRMATIONS

**Research based on:** Typical Devpost platform requirements, Google AI competition guidelines (ai.google.dev/competition), ADK hackathon patterns, and 100+ successful hackathon submissions.

**CONFIRM AT BRIEFING (12:30):**
- [ ] Exact submission platform URL
- [ ] Required fields for this event
- [ ] Judging timeline (if not Monday)
- [ ] Whether live demo round exists or just video submissions
- [ ] Where to send live demo link if platform is down

---

**Built: 22 August 2026, 13:30 GMT**
**Team: UK AI Agent Lab, DeepMind London**
