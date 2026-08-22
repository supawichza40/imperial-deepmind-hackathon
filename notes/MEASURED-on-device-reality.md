# MEASURED on this machine — on-device Gemma reality check

**Status: `observed`.** Run on the team's own M1 Mac, 16 GB RAM, 22 Aug 2026 ~12:15.
This overrides the performance estimate in `docs/05-gemma-4-on-device.md`, which was
`derived` from published sources and is wrong for this hardware.

## What was measured

Model: `gemma4:latest` (9.6 GB) — note `gemma4:latest` and `gemma4:e4b` resolve to the
**same** blob ID `c6eb396dbd59`. Two tags, one model.

Command: `echo "Explain what an AI agent is in exactly two sentences." | ollama run gemma4:latest --verbose`

| Metric | Measured |
|---|---|
| **Generation rate** | **4.74 tokens/s** |
| Prompt eval rate | 8.15 tokens/s |
| Model load (cold) | 65 s |
| Total for a 2-sentence answer | 2 min 9 s |
| Output tokens | 287 (most spent on visible chain-of-thought) |

Doc estimate was 50-80 tok/s. Measured is **~10x slower**.

## What this means for today

A live on-device demo at 4.7 tok/s is **not stage-viable** if it generates more than a
short sentence in front of judges. A 90-second demo window cannot absorb a 65-second
cold load plus a minute of generation.

If you still want the on-device angle (ideas #3, #7, #8, #10 in `docs/08`), do these:

1. **Keep the model warm.** Load it before the demo starts; never pay the 65 s cold load
   on stage. `ollama run gemma4:latest ""` during setup.
2. **Cap output hard.** Ask for one sentence, a label, a JSON field — not prose.
   At 4.7 tok/s every token costs a fifth of a second on screen.
3. **Suppress the thinking tokens.** The model reasons visibly by default and most of the
   287 tokens went there. Cut that and effective speed roughly triples.
4. **Try the E2B edge tier** (`gemma4:e2b`) — smaller, should be materially faster.
   Pull was still running at 12:18; benchmark before committing to it.
5. **Pre-record the on-device segment.** This is the single highest-risk part of any
   local demo and the one judges are least able to verify live anyway.

## Honest recommendation

On-device Gemma is still a strong *story* for this room and plays to Ian Ballantyne's
own track record. But on this laptop it is a **classification / short-answer** demo, not
a generation demo. Design the wow moment around "it answered with no network", not
around "watch it write".

If the demo needs fluent generated text, put Gemini 3.7 Flash on that path and use Gemma
for the offline claim.
