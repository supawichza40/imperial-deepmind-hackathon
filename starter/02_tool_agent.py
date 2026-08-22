"""02 - Tool-using agent (automatic function calling)

Gives the model three real Python functions as tools:
  - read_support_note(): reads a local file  (a "file reader" tool)
  - get_account_balance(): a fake-but-realistic internal API
  - calculate(): a small, safe arithmetic calculator

Pass plain Python functions straight into GenerateContentConfig(tools=[...])
and the SDK's automatic function calling loop reads their type hints and
docstrings, decides which to call and in what order, executes them, and
feeds the results back to the model — no manual dispatch loop needed.

Each tool prints itself when it's actually invoked, so a demo audience can
watch the agent reason and act step by step instead of just seeing a final
answer appear.

Run:
    python 02_tool_agent.py
"""
import ast
import operator
import os

from google.genai import types

from utils import (
    DEFAULT_MODEL,
    get_client,
    print_header,
    print_tool_call,
    print_usage,
    with_retry,
)

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
    """Evaluate a restricted arithmetic AST — no names, no calls, no attribute
    access, so a model-generated expression can't do anything but arithmetic."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"unsupported expression near: {ast.dump(node)}")


def read_support_note(filename: str) -> dict:
    """Reads a local support-ticket note by filename.

    Args:
        filename: name of the file inside the sample_data/ folder, e.g. "ticket_482.txt".

    Returns:
        A dict with the file's text content, or an error message.
    """
    path = os.path.join(SAMPLE_DATA_DIR, os.path.basename(filename))
    if not os.path.isfile(path):
        result = {"error": f"no such file: {filename}"}
    else:
        with open(path, "r") as f:
            result = {"content": f.read().strip()}
    print_tool_call("read_support_note", {"filename": filename}, result)
    return result


def get_account_balance(account_id: str) -> dict:
    """Looks up the current balance for an account in the internal ledger.

    Args:
        account_id: account identifier, e.g. "ACC-1009".

    Returns:
        A dict with balance and currency, or an error message.
    """
    result = _ACCOUNTS.get(account_id, {"error": f"unknown account: {account_id}"})
    print_tool_call("get_account_balance", {"account_id": account_id}, result)
    return result


def calculate(expression: str) -> dict:
    """Evaluates a basic arithmetic expression: + - * / ** and parentheses.

    Args:
        expression: an arithmetic expression, e.g. "128.32 + 45.50".

    Returns:
        A dict with the numeric result, or an error message.
    """
    try:
        value = _safe_eval(ast.parse(expression, mode="eval").body)
        result = {"result": value}
    except Exception as e:
        result = {"error": str(e)}
    print_tool_call("calculate", {"expression": expression}, result)
    return result


@with_retry()
def run_agent(client, prompt: str):
    config = types.GenerateContentConfig(
        tools=[read_support_note, get_account_balance, calculate],
    )
    return client.models.generate_content(model=DEFAULT_MODEL, contents=prompt, config=config)


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

    response = run_agent(client, prompt)

    print("\nfinal answer:")
    print(f"  {response.text}\n")
    print_usage(response.usage_metadata)


if __name__ == "__main__":
    main()
