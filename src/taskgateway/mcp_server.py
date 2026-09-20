"""Official MCP SDK v2 STDIO adapter for TaskGateway-Local.

The MCP dependency is intentionally imported only by this module so that the
core package remains zero-dependency and can be installed without MCP.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from .core import TaskGateway


def create_server(gateway: TaskGateway) -> MCPServer:
    """Create a v2 MCP server bound to one configured gateway."""
    server = MCPServer(
        name="taskgateway",
        version="1.0.0",
        description="Read-only search, planning, and fail-closed invocation rendering.",
        instructions="invoke renders commands only; it never executes them.",
    )
    annotations = ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )

    @server.tool(
        name="taskgateway_search",
        description="Search the configured TaskGateway resource index.",
        annotations=annotations,
        structured_output=True,
    )
    def taskgateway_search(query: str, limit: int = 10) -> dict[str, Any]:
        return gateway.search(query, limit)

    @server.tool(
        name="taskgateway_plan",
        description="Plan a deterministic route and evaluate the side-effect budget.",
        annotations=annotations,
        structured_output=True,
    )
    def taskgateway_plan(
        goal: str,
        intent: Literal["discover", "read", "write", "execute", "evaluate"] = "read",
        side_effect_budget: Literal[
            "none", "read_only", "bounded_write", "bounded_execute"
        ] = "read_only",
    ) -> dict[str, Any]:
        return gateway.plan(goal, intent, side_effect_budget)

    @server.tool(
        name="taskgateway_invoke",
        description="Render a call string after validating the decision binding; never execute.",
        annotations=annotations,
        structured_output=True,
    )
    def taskgateway_invoke(
        resource_ref: str,
        decision_id: str,
        operation: str = "render_call",
    ) -> dict[str, Any]:
        return gateway.invoke(resource_ref, decision_id, operation)

    return server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, required=True)
    args = parser.parse_args(argv)
    create_server(TaskGateway(args.index)).run("stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
