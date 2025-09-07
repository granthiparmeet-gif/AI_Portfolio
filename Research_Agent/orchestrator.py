from __future__ import annotations
import os, sys, asyncio
from pathlib import Path
from typing import Any, Dict, List
from agents import Agent, Runner
from agents.models.openai import OpenAIResponsesModel
from agents.tools import WebSearchTool, HostedMCPTool
from agents.mcp.server import MCPServerStdio, MCPServerStdioParams
from common.logger import get_logger
from common.exceptions import PlanError, MCPServerError

logger = get_logger(__name__)

INSTRUCTIONS = (
    "You are a meticulous research assistant.\n"
    "Use web_search to find sources; when needed, call http_get (MCP) to fetch page text.\n"
    "Answer with 6-10 concise bullets and include inline markdown links [n].\n"
    "If the user requests, call save_brief(topic, content) to persist the summary."
)

def _mcp_stdio() -> MCPServerStdio:
    server_py = Path(__file__).resolve().parents[0] / "mcp_server" / "server.py"
    repo_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = f"{repo_root}:{env.get('PYTHONPATH','')}"
    return MCPServerStdio(MCPServerStdioParams(
        command=sys.executable,
        args=[str(server_py)],
        env=env,
        cwd=str(server_py.parent),
    ))

async def _build_agent() -> Agent:
    model = OpenAIResponsesModel(model=os.getenv("RESEARCH_MODEL", "gpt-4o-mini"),
                                 api_key=os.environ["OPENAI_API_KEY"])
    return Agent(
        name="research_agent",
        instructions=INSTRUCTIONS,
        model=model,
        tools=[WebSearchTool(), HostedMCPTool(server=_mcp_stdio())],
    )

async def run_research_async(query: str) -> Dict[str, Any]:
    if not query or not query.strip():
        raise PlanError("Empty query.")
    try:
        agent = await _build_agent()
        result = await Runner.run(agent, input=query.strip(), max_turns=8)
        final = (result.final_output or "").strip()
        if not final:
            raise PlanError("No final answer produced.")
        hints: List[str] = []
        for it in result.new_items:
            out = getattr(it, "output", None)
            if isinstance(out, str) and "http" in out:
                hints.append(out[:1200])
        return {"answer": final, "sources_hint": hints[:8]}
    except Exception as e:
        logger.exception("Research agent failed")
        raise MCPServerError(str(e)) from e

def run_research(query: str) -> Dict[str, Any]:
    try:
        return asyncio.run(run_research_async(query))
    except PlanError as e:
        logger.error(f"PlanError: {e}")
        return {"answer": f"Error: {e}", "sources_hint": []}
