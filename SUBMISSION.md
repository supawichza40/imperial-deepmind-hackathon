# Submission — UK AI Agent Lab: Gemini Edition

**Deadline: 17:30 GMT SHARP.** Submit by 17:10. All four items are required.

## Checklist

- [ ] **1. Public GitHub repo** — clean code, informative README, setup instructions,
      architecture diagram, MIT or Apache licence
      - [x] Apache-2.0 licence (`LICENSE`)
      - [x] Architecture diagram (mermaid, in `README.md`)
      - [x] README filled in (all `TODO` markers gone)
      - [ ] Setup instructions verified by someone who didn't write them
      - [ ] Push to a public remote and paste the URL below
- [x] **2. Proof of model integration** — Gemini 3.7 Flash via Google GenAI SDK,
      and/or Gemma 4 via local runtime. Named with file and function in the README table.
      Both verified with live calls, not just written down (see README "Measured
      performance").
- [ ] **3. 2-minute demo video** — Loom or YouTube. Working prototype, core user flow,
      what it actually does. **Record by 16:45.** Upload processing can take 10+ minutes.
- [x] **4. Write-up, 2–3 paragraphs** — below.

## Track

**Track 3 — Best Hybrid AI & Human-Centric Utility.**

## Write-up

### The problem

Sharing a payslip or bank statement to prove income, dispute a bill, or ask for help
means handing over a document full of things the recipient doesn't need: a national
insurance number, a full address, an account number. Today that's an all-or-nothing
choice, so people either overshare sensitive fields they didn't need to, or don't share
the document at all and lose out on the help. Privacy Gate turns that into a field by
field decision, with a record of exactly what was approved and what wasn't.

### Architecture choices

A FastAPI backend exposes four stateless REST endpoints matching the four steps of the
flow: `/api/detect`, `/api/sanitise`, `/api/reason`, `/api/audit`. Detection runs a
deterministic regex layer for the structured cases (account numbers, National Insurance
numbers, postcodes, emails, phone numbers) alongside a language model call for the
fields regex cannot see, asked for structured JSON output (a list of matched substrings
and field types, not offsets or rewritten prose) so the local model's short, fast output
stays fast even on modest hardware. Python resolves character offsets from those
substrings with a best-match search that tracks already-claimed spans, since the model
can return fields out of document order or repeat a substring that appears more than
once in the text. A two-pass merge then resolves overlapping detections, keeping the
longer span when two different field types claim the same text. Only after a human
approves each field type does a sanitised payload get assembled and sent to Gemini for
cross-document reasoning; the consent step, not the redaction step alone, is what makes
this defensible rather than a wrapper over an existing local-redact-then-cloud-answer
pattern. The existing export module turns approved fields into a downloadable zip
(sanitised HTML, plain text, `audit.json`, and a passphrase-locked encrypted vault for
anything marked "encrypt" rather than "keep" or "blacklabel"), so the whole thing works
as ordinary files that open anywhere, with nothing expiring and nothing phoning home.

### Why Gemini and Gemma

Gemini 3.7 Flash, called through the Google GenAI SDK's Interactions API, does the
reasoning: comparing documents, finding inconsistencies, explaining them plainly, and
drafting a response. That's a job a fast frontier model is well suited for, and it
carries no privacy cost once it only ever sees the approved subset of a document.
Gemma's job is different: catching the free-text cases a regex cannot, like a name
mentioned in context or an unlabelled disclosure, which needs language understanding but
should stay cheap and fast since it runs before a human even sees the result. The build
originally planned a locally-pulled `gemma4:e2b` for that step so the detection pass
never touched the network; that pull did not finish on the build machine in time, so the
build measured and switched to Ollama's cloud-routed `gemma4:31b-cloud` tag instead, same
native API, same request shape, only the model name changed. That is an honest trade
made under a hard deadline, not a claim to hide: the regex layer still runs fully
on-device with no network dependency, and the architecture is built so that a smaller,
faster local pull can be dropped back in without touching the API layer at all.

### Future roadmap

1. Bring the field-detection language model call back fully on-device once a small
   enough local pull is verified fast on real hardware, restoring the stronger
   "nothing leaves the machine until you approve it" claim end to end.
2. Extend detection past the two synthetic fixture documents to arbitrary uploads,
   including image and PDF ingestion through Gemma's vision path.
3. Surface per-field detection confidence in the consent UI, so a low-confidence match
   gets flagged for extra scrutiny instead of presented with the same weight as a
   regex-certain one.

## Links

| Item | Link |
|---|---|
| Repo | https://github.com/supawichza40/imperial-deepmind-hackathon |
| Demo video | _TODO, record by 16:45_ |
| Live deployment (optional) | not applicable, runs locally |

## Timing

| Time | Gate |
|---|---|
| 15:00 | Draft submission created, even if empty |
| 16:00 | Feature freeze — polish only |
| 16:45 | Video recorded and uploading |
| 17:10 | **Submitted** |
| 17:30 | Deadline |
