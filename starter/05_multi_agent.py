"""05 - Multi-agent: orchestrator + 2 specialists

No framework (no ADK, no LangChain) - just plain Gemini calls with a
different system_instruction per role, wired together in Python. This is
deliberately low-tech so it still works even if a heavier agent framework
fails to install mid-hackathon.

Built on the Interactions API (client.interactions.create), Google's current
recommended surface (GA since June 2026) - system_instruction is a direct
keyword argument, same idea as GenerateContentConfig.system_instruction on
the legacy surface (see the commented fallback at the bottom).

Pattern:
  orchestrator -> decides what to hand the researcher
  researcher   -> gathers a few concrete facts
  writer       -> turns those facts into a punchy pitch
  orchestrator -> returns the writer's output as the final answer

Run:
    python 05_multi_agent.py
"""
from utils import DEFAULT_MODEL, get_client, print_header, print_interaction_usage, with_retry

RESEARCHER_INSTRUCTIONS = (
    "You are a research specialist. Given a topic, list 3 concrete, specific "
    "facts or ideas about it. Be terse - bullet points only, no preamble."
)

WRITER_INSTRUCTIONS = (
    "You are a writing specialist. Given a set of bullet-point facts, turn "
    "them into a punchy 2-sentence pitch. No bullet points in your output."
)

ORCHESTRATOR_INSTRUCTIONS = (
    "You are a project lead splitting a task between two specialists: a "
    "researcher and a writer. Given a user request, output ONLY the research "
    "topic to hand to the researcher - one line, no other text."
)


# A specialist here doesn't have to be a plain model call - Google's managed
# agents (Deep Research, Antigravity) are hosted agents you call through this
# same client.interactions.create(), just by swapping `model=`. e.g. to give
# the researcher role a real hosted web-research agent instead of a single
# generate call:
#
#   researcher_interaction = client.interactions.create(
#       model="deep-research-preview-04-2026",   # or antigravity-preview-05-2026
#       input=topic,
#   )
#
# Verified real model IDs (ai.google.dev/api/interactions-api): deep-research
# -pro-preview-12-2025, deep-research-preview-04-2026, deep-research-max
# -preview-04-2026, antigravity-preview-05-2026. Not wired in below to keep
# this demo fast and dependency-free - swap it in if you want a beefier
# researcher.


def _call(client, system_instruction: str, prompt: str):
    @with_retry()
    def _do():
        return client.interactions.create(
            model=DEFAULT_MODEL,
            input=prompt,
            system_instruction=system_instruction,
        )
    return _do()


def main():
    client = get_client()
    user_request = (
        "We need a 2-sentence pitch for a hackathon project that uses Gemini "
        "function calling for customer support."
    )

    print_header("05 - Multi-agent orchestration")
    print(f"model: {DEFAULT_MODEL}")
    print(f"user request: {user_request}\n")

    print("[orchestrator] deciding the research topic...")
    orchestrator_interaction = _call(client, ORCHESTRATOR_INSTRUCTIONS, user_request)
    topic = orchestrator_interaction.output_text.strip()
    print(f"  -> research topic: {topic!r}\n")

    print("[researcher] gathering facts...")
    researcher_interaction = _call(client, RESEARCHER_INSTRUCTIONS, topic)
    facts = researcher_interaction.output_text.strip()
    print(f"{facts}\n")

    print("[writer] turning facts into a pitch...")
    writer_interaction = _call(client, WRITER_INSTRUCTIONS, facts)
    pitch = writer_interaction.output_text.strip()
    print(f"{pitch}\n")

    print("[orchestrator] final answer:")
    print(f"  {pitch}\n")

    usages = [
        getattr(i, "usage", None)
        for i in (orchestrator_interaction, researcher_interaction, writer_interaction)
    ]
    print_interaction_usage(usages)


# --- Legacy fallback (generateContent) --------------------------------------
# Still fully supported - swap _call's body for this if `client.interactions`
# isn't available on your installed SDK:
#
# from google.genai import types
#
# def _call_legacy(client, system_instruction: str, prompt: str):
#     @with_retry()
#     def _do():
#         return client.models.generate_content(
#             model=DEFAULT_MODEL,
#             contents=prompt,
#             config=types.GenerateContentConfig(system_instruction=system_instruction),
#         )
#     return _do()
#
# # then read `.text` instead of `.output_text`, and `.usage_metadata` via
# # utils.print_usage instead of `.usage` via utils.print_interaction_usage.


if __name__ == "__main__":
    main()
