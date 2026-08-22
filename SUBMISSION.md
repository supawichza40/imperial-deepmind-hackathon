# Submission, UK AI Agent Lab: Gemini Edition

**Deadline: 17:30 GMT SHARP.** Submit by 17:10. All four items are required.

## Checklist

- [ ] **1. Public GitHub repo**: clean code, informative README, setup instructions,
      architecture diagram, MIT or Apache licence
      - [x] Apache-2.0 licence (`LICENSE`)
      - [x] Architecture diagram (mermaid, in `README.md`)
      - [ ] README filled in (all `TODO` markers gone)
      - [ ] Setup instructions verified by someone who didn't write them
- [ ] **2. Proof of model integration**: Gemini 3.7 Flash via the Google GenAI SDK,
      and/or Gemma 4 via local runtime. Named with file and function in the README table.
- [ ] **3. 2-minute demo video**: Loom or YouTube. Working prototype, core user flow,
      what it actually does. **Record by 16:45.** Upload processing can take 10+ minutes.
- [ ] **4. Write-up, 2–3 paragraphs**. See below.

## Track

**Track 3, Best Hybrid AI & Human-Centric Utility.**

## Write-up

### The problem

People routinely need help with documents they cannot hand to a cloud model: payslips,
bank statements, medical letters, immigration paperwork. Today the choice is binary. Paste
the whole thing in and hope, or get no help at all. Most people take the first option
without ever seeing what they disclosed. The document is the unit of sharing, so consent
is all or nothing, and the sensitive parts travel with the useful parts.

### Architecture choices

Privacy Gate splits the work at the point where the data would otherwise leave. Gemma 4
runs on the machine through Ollama's native generate route and returns a span map, matched
substrings plus a type, which Python resolves to character offsets. A deterministic
pattern matcher sits underneath it for account numbers, postcodes, national insurance
numbers and emails, so detection degrades to something useful rather than to nothing if
the model is unavailable. The user then approves each kind of information, and only the
approved subset is composed into a new document and sent to Gemini 3.7 Flash through the
Interactions API for cross document reasoning. An audit trail records what stayed and what
went. Measured on the build machine, an M1 with 16GB: detection returns 8 spans in roughly
4.5 seconds, every offset verified against the source text.

The consent step, not the redaction step, is what we think is defensible. Local redaction
followed by a cloud answer is a published pattern. Asking the person what each field would
let a stranger do, and letting them decide field type by field type, is not something we
found shipping anywhere.

### Why Gemini and Gemma specifically

Gemma 4 is used because it is open weights and runs locally, which is the only way the
guarantee holds. If redaction ran in the cloud, the original document would already have
left before consent existed, and the product would be a promise rather than a mechanism.
We deliberately kept the E2B variant on device rather than switching to a faster hosted
Gemma tag, because the hosted tag would have quietly broken exactly that claim.

Gemini 3.7 Flash handles what comes after the gate: reading several documents at once,
finding the inconsistency between them, and drafting a response. That work benefits from a
frontier model and carries no privacy cost once the identifying fields are gone.

The interface shows each field as a consequence rather than a label. Not "account number"
but "lets someone set up a direct debit in your name". Same detection, but the decision
becomes a judgement about risk instead of a labelling exercise.

### What we would not claim

This is assisted redaction with human approval, not guaranteed anonymisation. It can miss
things, which is precisely why a person approves every field type before anything is sent,
and why the audit trail exists.

### Future roadmap

1. Images and PDFs. Detection is text only today, and most people photograph a payslip
   rather than export it.
2. A learned consequence model, so the risk explanation is specific to the document rather
   than drawn from a fixed table.
3. Batch handling for a folder of documents, with the same per field consent applied once
   and reused, so the gate scales to a real filing cabinet.

## Links

| Item | Link |
|---|---|
| Repo | https://github.com/supawichza40/imperial-deepmind-hackathon |
| Demo video | _paste the Loom or YouTube link here the moment it uploads_ |
| Live deployment (optional) | runs locally: `.venv/bin/python3 app/server.py 8000` |

## Timing

| Time | Gate |
|---|---|
| 15:00 | Draft submission created, even if empty |
| 16:00 | Feature freeze, polish only |
| 16:45 | Video recorded and uploading |
| 17:10 | **Submitted** |
| 17:30 | Deadline |
