# Demo fallback checklist

A live demo dies from three things: network, rate limits, and an improvised
prompt. Handle all three before your slot, not during it.

## Before you're on stage

- [ ] Run every script once end-to-end at least an hour before your slot.
- [ ] Pre-record a 60-90s screen capture of the golden-path demo working. If
      wifi or the API dies, play the video instead of debugging live.
- [ ] Pull the local fallback model early, while wifi is still good:
      `ollama pull gemma3:4b`. Then test `07_local_gemma.py` with wifi OFF to
      confirm it actually works offline.
- [ ] Write down the exact prompts you'll type (paper, not just a file).
      Never improvise a new prompt live - that's the #1 way to hit an edge
      case in front of judges.
- [ ] Keep "live" data as static seed files (see `sample_data/`) instead of a
      real API/DB call you don't control.

## Defensive code already in this kit

- `utils.with_retry()` - exponential backoff on 429 (rate limit) and
  500/503 (server overloaded), so a transient blip doesn't kill the demo.
- `utils.get_client()` - fails with a plain-English message if the API key
  is missing, instead of a stack trace mid-pitch.
- Every `0X_*.py` script is standalone - one script crashing doesn't take
  the others down with it.
- `07_local_gemma.py` - a no-wifi-needed escape hatch.

## On stage

- [ ] Have a tested phone hotspot ready as backup network.
- [ ] Keep the pre-recorded video open in another tab, ready to alt-tab to.
- [ ] If a call hangs more than ~5 seconds, Ctrl+C it and either retry once
      or cut straight to the fallback video - don't let dead air eat your
      slot.
- [ ] Decide which single demo is your "must-work" one and rehearse that one
      until your hands know it without thinking.
