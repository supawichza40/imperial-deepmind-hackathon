"""07 - Local Gemma via Ollama (offline fallback)

If the Gemini API rate-limits or the venue wifi dies mid-pitch, fall back to
a local Gemma model served by Ollama through its OpenAI-compatible endpoint.
Same call shape as the OpenAI SDK - nothing Gemini-specific, and it needs no
internet once the model is pulled.

Setup (once, before the demo, while you still have wifi):
    brew install ollama
    ollama serve &          # or just open the Ollama app
    ollama pull gemma3:4b   # ~3GB download; pick a size that fits your RAM

Run:
    python 07_local_gemma.py
"""
import sys

from openai import OpenAI

MODEL = "gemma3:4b"
BASE_URL = "http://localhost:11434/v1"


def main():
    # api_key is required by the OpenAI SDK's constructor but ignored by Ollama.
    client = OpenAI(base_url=BASE_URL, api_key="ollama")

    print("=" * 32)
    print("07 - Local Gemma (Ollama, offline)")
    print("=" * 32)
    print(f"model: {MODEL} @ {BASE_URL}\n")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": "In one sentence, why is a local model a good demo fallback?",
                }
            ],
        )
    except Exception as e:
        sys.exit(
            f"\n[setup error] couldn't reach Ollama at {BASE_URL}: {e}\n"
            "  1. Install: brew install ollama\n"
            "  2. Start it: ollama serve\n"
            f"  3. Pull the model: ollama pull {MODEL}\n"
        )

    print("response:")
    print(f"  {response.choices[0].message.content}\n")

    usage = response.usage
    if usage:
        print(
            f"  tokens -> prompt: {usage.prompt_tokens} "
            f"| output: {usage.completion_tokens} | total: {usage.total_tokens}"
        )


if __name__ == "__main__":
    main()
