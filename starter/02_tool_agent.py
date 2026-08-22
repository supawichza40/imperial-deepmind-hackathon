"""02 - Tool-using agent (multi-step tool calling)

Gives the model three real Python functions as tools:
  - read_support_note(): reads a local file  (a "file reader" tool)
  - get_account_balance(): a fake-but-realistic internal API
  - calculate(): a small, safe arithmetic calculator

Built on the Interactions API (client.interactions.create) - Google's
current, recommended surface (GA since June 2026). One thing it does NOT do
(yet) that the older generateContent surface does: automatic function
calling. Interactions API hands back one function_call step at a time; you
run the tool and post the result back yourself. So this file implements
that loop in a few lines of Python (run_agent, below) and prints every step
so a demo audience can watch the agent reason and act.

A fully-automatic alternative exists on the legacy generateContent surface -
pass raw Python functions and the SDK loops for you - see the commented
fallback block at the bottom, useful if your installed SDK predates
Interactions API support.

Run:
    python 02_tool_agent.py
"""
import ast
import json
import operator
import os

from utils import DEFAULT_MODEL, get_client, print_header, print_interaction_usage, print_tool_call, with_retry

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")

# Fake-but-realistic internal API: an account ledger a real support tool might call.
_ACCOUNTS = {
    "ACC-1009": {"balance": 128.32, "currency": "USD"},
    "ACC-2044": {"balance": 512.00, "currency": "USD"},
    "ACC-3311": {"balance": 76.50, "currency": "GBP"},
}

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _safe_eval(node):
    """Evaluate a restricted arithmetic AST - no names, no calls, no attribute
    access, so a model-generated expression can't do anything but arithmetic."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"unsupported expression near: {ast.dump(node)}")


def read_support_note(filename: str) -> dict:
    """Reads a local support-ticket note by filename from sample_data/."""
    path = os.path.join(SAMPLE_DATA_DIR, os.path.basename(filename))
    if not os.path.isfile(path):
        result = {"error": f"no such file: {filename}"}
    else:
        with open(path, "r") as f:
            result = {"content": f.read().strip()}
    print_tool_call("read_support_note", {"filename": filename}, result)
    return result


def get_account_balance(account_id: str) -> dict:
    """Looks up the current balance for an account in the internal ledger."""
    result = _ACCOUNTS.get(account_id, {"error": f"unknown account: {account_id}"})
    print_tool_call("get_account_balance", {"account_id": account_id}, result)
    return result


def calculate(expression: str) -> dict:
    """Evaluates a basic arithmetic expression: + - * / ** and parentheses."""
    try:
        value = _safe_eval(ast.parse(expression, mode="eval").body)
        result = {"result": value}
    except Exception as e:
        result = {"error": str(e)}
    print_tool_call("calculate", {"expression": expression}, result)
    return result


TOOL_IMPLS = {
    "read_support_note": read_support_note,
    "get_account_balance": get_account_balance,
    "calculate": calculate,
}

# Interactions API tool declarations: the same JSON-schema shape as classic
# function_declarations, with a top-level "type": "function" discriminator
# (verified against ai.google.dev/gemini-api/docs/function-calling).
TOOL_DECLARATIONS = [
    {
        "type": "function",
        "name": "read_support_note",
        "description": "Reads a local support-ticket note by filename from the sample_data/ folder.",
        "parameters": {
            "type": "object",
            "properties": {"filename": {"type": "string", "description": "e.g. 'ticket_482.txt'"}},
            "required": ["filename"],
        },
    },
    {
        "type": "function",
        "name": "get_account_balance",
        "description": "Looks up the current balance for an account in the internal ledger.",
        "parameters": {
            "type": "object",
            "properties": {"account_id": {"type": "string", "description": "e.g. 'ACC-1009'"}},
            "required": ["account_id"],
        },
    },
    {
        "type": "function",
        "name": "calculate",
        "description": "Evaluates a basic arithmetic expression: + - * / ** and parentheses.",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "e.g. '128.32 + 45.50'"}},
            "required": ["expression"],
        },
    },
]


@with_retry()
def _create(client, history):
    return client.interactions.create(
        model=DEFAULT_MODEL,
        store=False,
        input=history,
        tools=TOOL_DECLARATIONS,
    )


def run_agent(client, prompt: str, max_steps: int = 6):
    """Drives the function_call <-> function_result loop by hand, since the
    Interactions API surfaces one tool call at a time instead of looping
    automatically. Returns (final_interaction, usage_per_call) once the model
    stops requesting tools, or when max_steps is hit as a safety valve."""
    history = [{"type": "user_input", "content": [{"type": "text", "text": prompt}]}]
    usages = []

    for _ in range(max_steps):
        interaction = _create(client, history)
        usages.append(getattr(interaction, "usage", None))
        for step in interaction.steps:
            history.append(step.model_dump())

        fc_step = next((s for s in interaction.steps if s.type == "function_call"), None)
        if fc_step is None:
            return interaction, usages

        tool_fn = TOOL_IMPLS[fc_step.name]
        result = tool_fn(**fc_step.arguments)
        history.append(
            {
                "type": "function_result",
                "name": fc_step.name,
                "call_id": fc_step.id,
                "result": [{"type": "text", "text": json.dumps(result)}],
            }
        )

    return interaction, usages


def main():
    client = get_client()
    prompt = (
        "Read the support note in 'ticket_482.txt'. Find which account needs "
        "a refund and how much. Look up that account's current balance, then "
        "calculate the new balance after the refund is added. Reply with one "
        "short summary sentence."
    )

    print_header("02 - Tool-using agent")
    print(f"model: {DEFAULT_MODEL}")
    print(f"task: {prompt}\n")
    print("agent reasoning + tool calls:")

    interaction, usages = run_agent(client, prompt)

    print("\nfinal answer:")
    print(f"  {interaction.output_text}\n")
    print_interaction_usage(usages)


# --- Legacy fallback (generateContent, TRUE automatic function calling) -----
# If `client.interactions` isn't available on your installed SDK, the older
# generateContent surface is actually simpler here: pass raw Python functions
# and the SDK runs the whole call/result loop for you, no manual history
# bookkeeping needed.
#
# from google.genai import types
# from utils import print_usage
#
# @with_retry()
# def run_agent_legacy(client, prompt: str):
#     config = types.GenerateContentConfig(
#         tools=[read_support_note, get_account_balance, calculate],
#     )
#     return client.models.generate_content(model=DEFAULT_MODEL, contents=prompt, config=config)
#
# response = run_agent_legacy(client, prompt)
# print(response.text)
# print_usage(response.usage_metadata)


if __name__ == "__main__":
    main()
