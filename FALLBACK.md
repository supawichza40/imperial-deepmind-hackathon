# FALLBACK - read this if the demo breaks on stage

## Step 0: pre-warm, before you walk on stage

```bash
ollama run gemma4:e2b ""
```

A cold load measured 16.6s and will sit inside the recording or the live demo if
you skip this. Run it once, right before you start, every time.

Confirm the model is actually there first if you have not touched this machine
today:

```bash
ollama list | grep gemma4
```

## The cached run: your instant undo button

Every screen can be replayed end to end from a pre-baked run with the network
off and no model calls. The data lives at
`app/static/gate/seed/demo-payload.json`.

**Open the gate page with `?demo=1` on the URL**, for example:

```
http://localhost:8000/static/gate/index.html?demo=1
```

(Confirm the actual port with whoever ran `app/server.py` before you go on. If
it is not wired up yet, jump straight to Plan B or C below.)

## If something breaks, in order

1. **Local model not responding.** Check `ollama ps`. If nothing is listed, run
   `ollama serve` in a spare terminal, then redo Step 0. If there is no time:
   click "Continue without the model" on screen. The regex fallback still
   catches account numbers, postcodes, NI numbers and emails, just not names in
   free text. Say this out loud, it is an honest answer, not a failure.
2. **No API key, or the cloud step errors.** Load the `?demo=1` URL above and
   keep talking over it. Say "here's a run I captured earlier" and move on,
   nobody will mind.
3. **Rate limited (429).** Same fix: `?demo=1`. Do not retry live on stage.
4. **Wifi is gone.** The local half (screens S1 to S5) keeps working with no
   network at all, that is the point, say so. For the cloud half (S6 to S8),
   switch to `?demo=1`.
5. **Laptop is slow / anything else looks wrong.** Stop clicking. Play the
   recorded fallback video or GIF instead and narrate over it.
6. **Everything is down, even the recording won't play.** Open
   `docs/visual/2026-08-22-privacy-gate-screens.html` in any browser. It is a
   full click-through mock of every screen (S1 to S8, plus the error states)
   with the real copy. Walk the judges through it directly, it is built to
   stand in for the live app.

## Seeded documents, for re-running any of this yourself

- `app/static/gate/seed/payslip-july.txt` - Priya Desai, Northbridge Retail
  Ltd, gross pay £2,840.00 for July 2026.
- `app/static/gate/seed/bank-statement-july.txt` - same person, same month,
  salary credit shown as £2,400.00. This is the deliberate mismatch: the
  finding the cloud step reports is that the payslip and the bank statement do
  not agree on income.

Both are invented people. Nothing here is a real payslip or bank statement.
