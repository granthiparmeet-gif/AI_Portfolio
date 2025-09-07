from __future__ import annotations
import os, json, httpx
from typing import Dict, Any
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from common.logger import get_logger

logger = get_logger(__name__)
mcp = FastMCP("research_mcp")

class SaveBriefArgs(BaseModel):
    topic: str = Field(..., description="Short title for the brief")
    content: str = Field(..., description="Markdown/text content to persist")

@mcp.tool()
def http_get(url: str, timeout: float = 12.0) -> Dict[str, Any]:
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("Only http/https URLs allowed")
    with httpx.Client(timeout=timeout, follow_redirects=True, headers={"User-Agent": "ResearchAgent/1.0"}) as client:
        r = client.get(url)
        r.raise_for_status()
        ctype = r.headers.get("content-type","")
        text = r.text if ("text" in ctype or "json" in ctype) else r.content.decode(errors="ignore")
        return {"url": str(r.request.url), "status": r.status_code, "content_type": ctype, "text": text[:50000]}

@mcp.tool()
def save_brief(args: SaveBriefArgs) -> Dict[str, str]:
    base = os.getenv("RESEARCH_BRIEFS_DIR", "./research_briefs")
    os.makedirs(base, exist_ok=True)
    safe = "".join(c for c in args.topic if c.isalnum() or c in (" ","_","-")).strip().replace(" ","_") or "brief"
    path = os.path.join(base, f"{safe}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"topic": args.topic, "content": args.content}, f, ensure_ascii=False, indent=2)
    logger.info(f"[MCP] Saved brief -> {path}")
    return {"path": path}
