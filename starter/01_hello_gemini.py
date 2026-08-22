"""01 - Hello Gemini

The simplest possible call: one prompt in, one response out, plus the token
usage for that call. If this runs, your key and environment are good and
every other script in this kit will work too.

Run:
    python 01_hello_gemini.py
"""
from utils import DEFAULT_MODEL, get_client, print_header, print_usage, with_retry


@with_retry()
def ask(client, prompt: str):
    return client.models.generate_content(model=DEFAULT_MODEL, contents=prompt)


def main():
    client = get_client()
    prompt = "In one sentence, why are AI agents useful at a hackathon?"

    print_header("01 - Hello Gemini")
    print(f"model: {DEFAULT_MODEL}")
    print(f"prompt: {prompt}\n")

    response = ask(client, prompt)

    print("response:")
    print(f"  {response.text}\n")
    print_usage(response.usage_metadata)


if __name__ == "__main__":
    main()
