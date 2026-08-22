"""01 - Hello Gemini

The simplest possible call: one prompt in, one response out, plus token
usage. Uses the Interactions API (client.interactions.create) - Google's
current, recommended surface for the Gemini API, GA since June 2026
(ai.google.dev/gemini-api/docs/interactions: "The Interactions API is the
best way to build with Gemini models and agents... recommended for all new
projects"). A commented fallback using the older but still fully-supported
generateContent surface is at the bottom of this file.

Run:
    python 01_hello_gemini.py
"""
from utils import DEFAULT_MODEL, get_client, print_header, print_interaction_usage, with_retry


@with_retry()
def ask(client, prompt: str):
    return client.interactions.create(model=DEFAULT_MODEL, input=prompt)


def main():
    client = get_client()
    prompt = "In one sentence, why are AI agents useful at a hackathon?"

    print_header("01 - Hello Gemini")
    print(f"model: {DEFAULT_MODEL}")
    print(f"prompt: {prompt}\n")

    interaction = ask(client, prompt)

    print("response:")
    print(f"  {interaction.output_text}\n")
    print_interaction_usage(interaction.usage)


# --- Legacy fallback (generateContent) --------------------------------------
# Still fully supported, just no longer the recommended entry point. Use this
# if `client.interactions` doesn't exist on your installed google-genai
# version (e.g. an older pin picked up by a venue-wifi `pip install`):
#
# from utils import print_usage
#
# @with_retry()
# def ask_legacy(client, prompt: str):
#     return client.models.generate_content(model=DEFAULT_MODEL, contents=prompt)
#
# response = ask_legacy(client, prompt)
# print(response.text)
# print_usage(response.usage_metadata)


if __name__ == "__main__":
    main()
