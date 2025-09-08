from fastmcp import FastMCP

# Define MCP server and custom tools
mcp = FastMCP("research_agent_mcp")

@mcp.tool()
def echo_tool(message: str) -> str:
    """Simple test tool to check MCP works"""
    return f"Echo: {message}"