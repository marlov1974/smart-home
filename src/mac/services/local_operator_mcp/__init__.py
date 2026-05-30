"""P0028 true MCP stdio adapter for the read-only local operator bridge."""

from .core import (
    MCP_PROTOCOL_VERSION,
    SERVER_INFO,
    McpError,
    call_mcp_tool,
    format_mcp_tool_result,
    handle_initialize,
    handle_initialized_notification,
    handle_mcp_message,
    list_mcp_tools,
    process_mcp_line,
    serve,
)

__all__ = [
    "MCP_PROTOCOL_VERSION",
    "SERVER_INFO",
    "McpError",
    "call_mcp_tool",
    "format_mcp_tool_result",
    "handle_initialize",
    "handle_initialized_notification",
    "handle_mcp_message",
    "list_mcp_tools",
    "process_mcp_line",
    "serve",
]
