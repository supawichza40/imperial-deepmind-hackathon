"""05 - Multi-agent: orchestrator + 2 specialists

No framework (no ADK, no LangChain) — just plain Gemini calls with a
different system_instruction per role, wired together in Python. This is
deliberately low-tech so it still works even if a heavier agent framework
fails to install mid-hackathon.

Pattern:
  orchestrator -> decides what to hand the researcher
  researcher   -> gathers a few concrete facts
  writer       -> turns those facts into a punchy pitch
  orchestrator -> returns the writer's output as the final answer

Run:
    python 05_multi_agent.py
"""
from google.genai import types

from utils import DEFAULT_MODEL, get_client, print_header, with_retry

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


def _call(client, system_instruction: str, prompt: str):
    @with_retry()
    def _do():
        return client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction),
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
    orchestrator_response = _call(client, ORCHESTRATOR_INSTRUCTIONS, user_request)
    topic = orchestrator_response.text.strip()
    print(f"  -> research topic: {topic!r}\n")

    print("[researcher] gathering facts...")
    researcher_response = _call(client, RESEARCHER_INSTRUCTIONS, topic)
    facts = researcher_response.text.strip()
    print(f"{facts}\n")

    print("[writer] turning facts into a pitch...")
    writer_response = _call(client, WRITER_INSTRUCTIONS, facts)
    pitch = writer_response.text.strip()
    print(f"{pitch}\n")

    print("[orchestrator] final answer:")
    print(f"  {pitch}\n")

    total_tokens = sum(
        r.usage_metadata.total_token_count
        for r in (orchestrator_response, researcher_response, writer_response)
        if r.usage_metadata is not None
    )
    print(f"  tokens used across all 3 agent calls: {total_tokens}")


if __name__ == "__main__":
    main()
