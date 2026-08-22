"""06 - Live API realtime agent (SKELETON)

The Live API opens a persistent, bidirectional session with the model over
a websocket - the building block for a voice agent. This file runs a
TEXT-only version by default so it needs no microphone/speaker setup to
demo; it shows exactly where to swap in real audio streaming.

Verified this session against ai.google.dev/gemini-api/docs/live-guide:
client.aio.live.connect(...), session.send_client_content(turns=...,
turn_complete=...), and session.receive() yielding
response.server_content.model_turn.parts. The audio swap-in below is
UNVERIFIED beyond that structure - the mic capture loop is standard PyAudio
boilerplate, not something fetched from Gemini docs this session.

Run:
    python 06_live_voice_agent.py

To go from this skeleton to full voice:
  1. pip install pyaudio   (needs `brew install portaudio` first on macOS)
  2. capture mic input as 16-bit PCM at 16kHz
  3. replace the send_client_content(...) call below with:
       await session.send_realtime_input(
           audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
       )
  4. set config["response_modalities"] = ["AUDIO"] and play back the
     returned part.inline_data.data bytes instead of printing part.text
"""
import asyncio

from utils import LIVE_MODEL, get_client, print_header

TURNS = [
    "Hi! In one sentence, what can you help me with?",
    "Great - now give me a one-line hackathon project idea using Gemini function calling.",
]


async def run_session():
    client = get_client()
    # Swap to ["AUDIO"] for real voice - see module docstring.
    config = {"response_modalities": ["TEXT"]}

    print_header("06 - Live API agent (text skeleton)")
    print(f"model: {LIVE_MODEL}\n")

    async with client.aio.live.connect(model=LIVE_MODEL, config=config) as session:
        for turn in TURNS:
            print(f"you: {turn}")
            await session.send_client_content(
                turns=[{"role": "user", "parts": [{"text": turn}]}],
                turn_complete=True,
            )

            print("gemini: ", end="", flush=True)
            async for response in session.receive():
                if response.server_content and response.server_content.model_turn:
                    for part in response.server_content.model_turn.parts:
                        if getattr(part, "text", None):
                            print(part.text, end="", flush=True)
                if response.server_content and response.server_content.turn_complete:
                    print()
                    break


def main():
    asyncio.run(run_session())


if __name__ == "__main__":
    main()
