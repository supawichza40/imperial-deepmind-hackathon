"""04 - Structured output (JSON extraction into a typed object)

Uses the Interactions API's response_format + a Pydantic model's JSON schema
to force the model to return JSON that matches a Python type exactly — no
regex, no "please respond in JSON" prompting hacks.

Run:
    python 04_structured_output.py
"""
from typing import List

from pydantic import BaseModel, Field

from utils import DEFAULT_MODEL, get_client, print_header, with_retry


class Session(BaseModel):
    """One talk/workshop slot at the hackathon."""
    title: str
    speakers: List[str] = Field(default_factory=list)
    time_range: str
    track: str


class Agenda(BaseModel):
    event_name: str
    sessions: List[Session]


RAW_TEXT = """
UK AI Agent Lab: Gemini Edition, London, 22 Aug 2026.
12:30 - Kickoff & rules, hosted by the DeepMind devrel team, Main Hall track.
13:00 - "Building agents with the Gemini API", talk by Priya Nair and Sam Cole, Main Hall track.
14:00 - Hacking begins, all tracks.
16:30 - "Judging criteria walkthrough", talk by Priya Nair, Workshop Room track.
17:30 - Demos & judging, all tracks.
"""


@with_retry()
def extract(client, text: str) -> Agenda:
    interaction = client.interactions.create(
        model=DEFAULT_MODEL,
        input=f"Extract the event schedule as structured data:\n\n{text}",
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": Agenda.model_json_schema(),
        },
    )
    return Agenda.model_validate_json(interaction.output_text)


def main():
    client = get_client()

    print_header("04 - Structured output")
    print(f"model: {DEFAULT_MODEL}")
    print("raw text ->")
    print(RAW_TEXT)

    agenda = extract(client, RAW_TEXT)

    print(
        f"parsed into Agenda(event_name={agenda.event_name!r}, "
        f"{len(agenda.sessions)} sessions):\n"
    )
    for s in agenda.sessions:
        print(f"  [{s.time_range}] {s.title}  ({s.track})")
        print(f"    speakers: {', '.join(s.speakers) or '(none listed)'}")

    print(f"\ntype check: agenda is Agenda            -> {isinstance(agenda, Agenda)}")
    print(f"type check: agenda.sessions[0] is Session -> {isinstance(agenda.sessions[0], Session)}")


# --- Legacy fallback (generateContent) --------------------------------------
# response_schema/response_mime_type predates the Interactions API and has
# been a stable generateContent feature for a long time, but wasn't
# independently re-checked against today's docs (marked UNVERIFIED for that
# reason) - sanity-check against ai.google.dev/gemini-api/docs/structured-output
# before relying on it:
#
# from google.genai import types
#
# @with_retry()
# def extract_legacy(client, text: str) -> Agenda:
#     response = client.models.generate_content(
#         model=DEFAULT_MODEL,
#         contents=f"Extract the event schedule as structured data:\n\n{text}",
#         config=types.GenerateContentConfig(
#             response_mime_type="application/json",
#             response_schema=Agenda,
#         ),
#     )
#     return Agenda.model_validate_json(response.text)


if __name__ == "__main__":
    main()
