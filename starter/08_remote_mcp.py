"""08 - Remote MCP server (native, zero client-side plumbing)

The Interactions API can call a Model Context Protocol (MCP) server
directly over HTTP: give it a URL (and optional auth headers) and Gemini
does the MCP handshake, tool listing, and tool calling itself. No local MCP
client, no stdio subprocess, no extra Python dependency.

Verified against the official REST reference (ai.google.dev/api/interactions-api):
the tool type is "mcp_server", with fields `url`, `name`, and an optional
`headers` dict for auth/timeouts. Streamable HTTP only - no SSE transport.

This demo points at DeepWiki's public MCP server: free, no auth required,
lets the model query documentation for any public GitHub repo.
    https://mcp.deepwiki.com/mcp

Other real remote MCP servers worth pointing at for your own project:
  - GitHub's official remote server (needs a GitHub PAT in headers):
      {"type": "mcp_server", "name": "github",
       "url": "https://api.githubcopilot.com/mcp/",
       "headers": {"Authorization": "Bearer <your GitHub PAT>"}}

Run:
    python 08_remote_mcp.py
"""
from utils import DEFAULT_MODEL, get_client, print_header, print_interaction_usage, with_retry

MCP_SERVER = {
    "type": "mcp_server",
    "name": "deepwiki",
    "url": "https://mcp.deepwiki.com/mcp",
}


@with_retry()
def ask_via_mcp(client, prompt: str):
    return client.interactions.create(
        model=DEFAULT_MODEL,
        input=prompt,
        tools=[MCP_SERVER],
    )


def main():
    client = get_client()
    prompt = "Using the DeepWiki MCP tool, what does the googleapis/python-genai repo do? One paragraph."

    print_header("08 - Remote MCP server (DeepWiki)")
    print(f"model: {DEFAULT_MODEL}")
    print(f"mcp server: {MCP_SERVER['url']}")
    print(f"prompt: {prompt}\n")

    interaction = ask_via_mcp(client, prompt)

    print("response:")
    print(f"  {interaction.output_text}\n")
    print_interaction_usage(getattr(interaction, "usage", None))


if __name__ == "__main__":
    main()
