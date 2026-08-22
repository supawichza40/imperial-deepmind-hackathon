# 11 — The idea sweep: a multi-agent workflow for finding what to build

Written 22 Aug 2026, after running it once under real deadline pressure at the UK AI
Agent Lab. This records the shape, what it cost, and the four things that went wrong,
so the next run starts from the corrected version rather than the designed one.

## What it is for

Turning an open-ended "what should we build" into a ranked, evidence-backed shortlist in
under an hour, when the honest answer is that nobody in the room knows yet and guessing
costs a whole afternoon.

It is not for narrowing an idea you already have. It is for the case where the space is
wide, the clock is short, and being wrong is expensive.

## The shape

```
LEAD
├── Plan gate — spawn tree + full plan table + budget, then STOP for approval
├── Wave 1 — 8 domain scouts, one per slice of everyday life
│     └── each spawns 2 children: PRIOR-ART hunter · FEASIBILITY prover
├── Wave 1 — independent cross-model runs, same brief, zero shared context
├── Wave 2 — 3 judges, one axis each: novelty · buildability · stage impact
├── Wave 3 — LEAD synthesis into one page a human reads in two minutes
└── Wave 4 — adversarial verifier, fresh context, no stake in the work
```

Thirty agents, about 1M tokens, roughly 25 minutes wall clock, around $69 of the session
total.

### Why each piece exists

**Domain slicing, not a general call for ideas.** Eight named territories — money and
admin, health, inbox, home and food, travel, work and learning, care, phone life and
accessibility — each assigned to exactly one scout with an explicit instruction not to
stray. Without this, parallel agents return the same four ideas. The territories are
what make thirty agents produce thirty agents' worth of coverage.

**Two children per scout, doing the two jobs a scout cannot do honestly.** One hunts
prior art; one proves the build. Both report back into the parent's file. This is where
most of the token spend goes and it is the part that earns it.

**Independent cross-model runs.** The same written brief handed to different models with
no shared context. Where they converge independently, that is signal. Where they
diverge, that is where the unbuilt ideas live. In this run the strongest single idea and
the best interaction device both came from the independent runs, not from the eight
scouts.

**One judge per axis, not one judge scoring everything.** Novelty, buildability and
stage impact pull in opposite directions, and a single judge quietly trades them off
inside its own head. Separated, the trade-off surfaces: the most buildable ideas were
text-only and dull, the best demos were camera-based and risky. The winner is whatever
scores decently on all three, which is never the top of any single list.

**A verifier with no stake, in fresh context.** Last, after the recommendation exists,
told to default to UNSUPPORTED without proof.

## The four things that went wrong

**1. Generators cannot clear their own novelty.** Four of eight scouts had their own top
pick killed by the independent novelty judge — on prior art each of them had explicitly
"checked". Not laziness: they searched, found something adjacent, and talked themselves
into the delta. Whoever produces an idea must never be the one who clears it. This is
now a structural rule, not a quality bar.

**2. The verifier has to execute, not review.** The recommendation said "spend twenty
minutes proving the local image call works." The verifier ran it instead, and found the
recommended model was the wrong one — 14.2s against 7.5s for its smaller sibling, where
the stated budget was 12s. A team following the written advice would have abandoned a
working idea. Any claim about runtime behaviour should be tested by the verifier, not
argued about.

**3. Facts in the brief go stale mid-flight.** The brief told all thirty agents that a
public login-free URL was required and a localhost demo scores as broken. That was
inferred from comparable events and it was wrong for this one — the actual requirement
was a repo, a video and a write-up. Every agent scored deployment risk against a
constraint that did not exist. When ground truth lands mid-run, re-score rather than
patching the summary.

**4. It finished after the build started.** By the time the portfolio existed, another
session was forty minutes into implementing something that was not on it. The right
answer was not to switch. A sweep that lands after commitment converts from "what should
we build" into "what should we change about what we are building", and its output has to
be rewritten in those terms or it is just noise.

## Running it again

1. **Write the brief as a file first**, then point every agent at it. One source of
   truth, cheap prompts, and a paste-ready artefact for any model outside the harness.
2. **Put the constraints that kill ideas in the brief, not in your head.** Frequency of
   use, prior-art evidence, the demo moment, what happens when the API throttles, the
   quotable number. Each one is a filter that runs thirty times for free.
3. **Present the plan and stop.** Spawn tree, full table, running token budget.
4. **Spawn wave 1 in a single message** so it runs concurrently.
5. **Workers return a file path and three lines**, never a transcript. The lead reads
   files, not conversations, or the lead's own context becomes the bottleneck.
6. **Correct workers mid-flight** when you verify something they are working from is
   wrong — they will re-score. One correction here rescued two ideas and correctly
   failed three others that rode a different unverified stack.
7. **Synthesise into one page**, not a folder of markdown. Nobody reads ten files at
   16:00.
8. **Verify last, adversarially, in fresh context**, and give it permission to say the
   recommendation is wrong. In this run it was half wrong, and that was the most
   valuable output of the whole exercise.

## Artefacts from the run

| File | What it holds |
|---|---|
| `notes/plans/2026-08-22-cross-model-prompt.md` | The brief. Reusable — replace the event facts. |
| `notes/plans/2026-08-22-idea-ocean.html` | The plan page shown at the approval gate. |
| `notes/ideas/*.md` | 56 candidates across 8 domains plus 2 independent model runs. |
| `notes/ideas/_judge-novelty.md` | 56 scored, 31 killed on prior art, with links. |
| `notes/ideas/_judge-buildable.md` | Scored against the real time remaining, not an ideal day. |
| `notes/ideas/_judge-wow.md` | Beat-by-beat demo staging for the top five. |
| `notes/ideas/_VERDICT.md` | Adversarial verification. Four FALSE findings. |
| `docs/visual/2026-08-22-idea-portfolio.html` | The synthesis, with its own corrections kept visible. |

## What it is worth

The sweep did not change what got built. Judged on that alone it failed.

What it produced instead was a proven local image call, a measured reason to switch
models, one interaction device worth stealing, and a documented warning that the build's
novelty claim was thinner than its own notes said. That is a reasonable return, but it
is a different return from the one the exercise was commissioned for — and the honest
version of this playbook says so rather than claiming the win it did not get.

Run it **before** anyone starts building, or accept that it becomes a review of work
already underway.
