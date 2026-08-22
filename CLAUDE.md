# Project instructions

UK AI Agent Lab, Gemini Edition. We are building **Privacy Gate**, a
consent-aware document agent, on Track 3.

## The rules live in one file

All build rules for this project are in `.claude/skills/privacy-gate/SKILL.md`,
imported below. That file is the single source of truth: edit it there and the
change is in force for every session that starts afterwards. Do not restate its
rules here, and do not keep a second copy anywhere else.

@.claude/skills/privacy-gate/SKILL.md

## Where the facts are

Read these before contradicting anything in them. They are ordered by
authority, and the organiser's own words win.

| File | Holds |
|---|---|
| `docs/00-ground-truth.md` | The organiser's schedule, speakers and prizes. |
| `docs/10-tracks-rules-rubric.md` | Tracks, rubric and submission rules, announced 12:30. Overrides any inference elsewhere. |
| `notes/ideas/privacy-gate.md` | What we are building and why, plus the upgrades decided at 14:05. |
| `notes/MEASURED-on-device-reality.md` | Real timings from this machine, not spec-sheet numbers. |
| `docs/11-idea-sweep-workflow.md` | How the idea sweep ran, and the four ways it went wrong. |

## Working here

- The deadline is **17:30 today** and it is hard. Scope accordingly.
- Several Claude sessions share this working tree. Before switching branches or
  merging, check `git status` and do the work in a temporary worktree rather
  than changing files under another session.
- `notes/playground/` is gitignored and disposable. Anything worth keeping goes
  in `docs/visual/`.
- Prove runtime claims by running them. Today a written recommendation named
  the wrong model, and only executing the call caught it.
