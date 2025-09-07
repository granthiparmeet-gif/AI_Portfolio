from __future__ import annotations
from mcp.server.fastmcp import run
from .tools import mcp

# Launched by the Agents SDK over STDIO.
if __name__ == "__main__":
    run(mcp)
