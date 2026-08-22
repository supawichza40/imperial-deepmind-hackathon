"""03 - Grounded agent (Google Search + URL context)

Uses two built-in Gemini tools via the Interactions API:
  - google_search: lets the model search the live web
  - url_context:   lets the model fetch and read a specific URL you give it

Every claim comes back with an inline citation to a real source, which this
script prints out — so you (or a judge) can verify the answer isn't a
hallucination.

Run:
    python 03_grounded_agent.py
"""
from utils import DEFAULT_MODEL, get_client, print_header, print_interaction_usage, with_retry

URL_TO_CHECK = "https://deepmind.google/"


@with_retry()
def ask_grounded(client, prompt: str):
    return client.interactions.create(
        model=DEFAULT_MODEL,
        input=prompt,
        tools=[{"type": "google_search"}, {"type": "url_context"}],
    )


def main():
    client = get_client()
    prompt = (
        f"Using {URL_TO_CHECK} and a live web search, what does Google "
        "DeepMind work on? Give me 3 bullet points, each backed by a source."
    )

    print_header("03 - Grounded agent (search + URL context)")
    print(f"model: {DEFAULT_MODEL}")
    print(f"prompt: {prompt}\n")

    interaction = ask_grounded(client, prompt)

    print("response:")
    for step in interaction.steps:
        if step.type != "model_output":
            continue
        for block in step.content:
            if block.type != "text":
                continue
            print(f"  {block.text}")
            if block.annotations:
                print("\ncitations:")
                for ann in block.annotations:
                    if ann.type == "url_citation":
                        cited = block.text[ann.start_index:ann.end_index]
                        print(f"  [{ann.title}]({ann.url})")
                        print(f'    cited: "{cited}"')

    print()
    print_interaction_usage(getattr(interaction, "usage", None))


# --- Legacy fallback (generateContent) --------------------------------------
# Still fully supported. Google Search grounding works the same way; URL
# context and the inline url_citation annotation shape shown above are
# Interactions-API-specific, so citation parsing differs - check
# ai.google.dev/gemini-api/docs/google-search for the classic
# grounding_metadata field names if you need this path:
#
# from google.genai import types
#
# @with_retry()
# def ask_grounded_legacy(client, prompt: str):
#     return client.models.generate_content(
#         model=DEFAULT_MODEL,
#         contents=prompt,
#         config=types.GenerateContentConfig(
#             tools=[types.Tool(google_search=types.GoogleSearch())]
#         ),
#     )
#
# response = ask_grounded_legacy(client, prompt)
# print(response.text)


if __name__ == "__main__":
    main()
