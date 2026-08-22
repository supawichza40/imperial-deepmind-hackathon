"""CLI entry point. Prints each stage so the pipeline is visible during a demo."""
import os
import sys

from pipeline import LOCAL_MODEL, run

BAR = "=" * 60


def main() -> None:
    user_input = " ".join(sys.argv[1:]).strip()
    if not user_input:
        sys.exit('usage: python app/main.py "your input here"')

    print(BAR)
    print("PROJECT_NAME")
    print(BAR)
    print(f'input: "{user_input}"\n')

    use_local = os.environ.get("LOCAL") == "1"
    if use_local:
        print(f"[1/2] local step  ({LOCAL_MODEL}, offline) ...", flush=True)
    else:
        print("[1/2] local step  skipped  (set LOCAL=1 to enable)")
    result = run(user_input, use_local=use_local)
    print(f"      -> {result['local_label']}\n")

    print("[2/2] cloud step  (gemini-3.7-flash) ...")
    print(f"      -> {result['response']}\n")
    print(BAR)


if __name__ == "__main__":
    main()
