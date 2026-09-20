from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

from mcp.types import CallToolResult

from taskgateway import TaskGateway
from taskgateway.mcp_server import create_server


def test_tools_have_names_schemas_and_read_only_annotations(fixture_index: Path) -> None:
    server = create_server(TaskGateway(fixture_index))

    tools = {tool.name: tool for tool in asyncio.run(server.list_tools())}

    assert set(tools) == {
        "taskgateway_search",
        "taskgateway_plan",
        "taskgateway_invoke",
    }
    assert tools["taskgateway_search"].input_schema["required"] == ["query"]
    assert tools["taskgateway_plan"].input_schema["required"] == ["goal"]
    assert tools["taskgateway_invoke"].input_schema["required"] == [
        "resource_ref",
        "decision_id",
    ]
    for tool in tools.values():
        assert tool.annotations.read_only_hint is True
        assert tool.annotations.destructive_hint is False
        assert tool.output_schema is not None


def test_in_memory_mcp_calls_return_structured_content(fixture_index: Path) -> None:
    server = create_server(TaskGateway(fixture_index))

    search_result = asyncio.run(
        server.call_tool("taskgateway_search", {"query": "readme resource"})
    )
    assert isinstance(search_result, CallToolResult)
    assert search_result.structured_content["response"]["data"]["n_hits"] == 1

    resource_ref = search_result.structured_content["response"]["data"]["results"][0]["ref"]
    plan_result = asyncio.run(
        server.call_tool("taskgateway_plan", {"goal": "readme resource"})
    )
    plan_data = plan_result.structured_content["response"]["data"]
    invoke_result = asyncio.run(
        server.call_tool(
            "taskgateway_invoke",
            {"resource_ref": resource_ref, "decision_id": plan_data["decision_id"]},
        )
    )
    assert invoke_result.structured_content["response"]["data"]["executed"] is False


def test_mcp_invoke_invalid_decision_id_is_blocked(fixture_index: Path) -> None:
    server = create_server(TaskGateway(fixture_index))

    result = asyncio.run(
        server.call_tool(
            "taskgateway_invoke",
            {"resource_ref": "tool://readme", "decision_id": "invalid"},
        )
    )

    payload = result.structured_content
    assert payload["response"]["status"] == "blocked"
    assert payload["response"]["errors"][0]["code"] == "DECISION_UNKNOWN"
    assert payload["response"]["data"]["executed"] is False


def test_mcp_plan_denies_budget_outside_read_only(fixture_index: Path) -> None:
    server = create_server(TaskGateway(fixture_index))

    result = asyncio.run(
        server.call_tool(
            "taskgateway_plan",
            {"goal": "readme resource", "side_effect_budget": "bounded_execute"},
        )
    )

    payload = result.structured_content
    assert payload["response"]["status"] == "blocked"
    assert payload["response"]["data"]["gate"]["decision"] == "ask_operator"
    assert payload["response"]["data"]["gate"]["reason_code"] == "AUTHORIZATION_REQUIRED"


def test_stdio_handshake_has_no_non_protocol_stdout(fixture_index: Path) -> None:
    process = subprocess.Popen(
        [sys.executable, "-m", "taskgateway.mcp_server", "--index", str(fixture_index)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path(__file__).parents[1],
        env={
            **os.environ,
            "PYTHONPATH": str(Path(__file__).parents[1] / "src"),
        },
    )
    assert process.stdin and process.stdout and process.stderr
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "0"},
        },
    }
    process.stdin.write(json.dumps(initialize) + "\n")
    process.stdin.flush()
    response_line = process.stdout.readline()
    process.kill()
    assert response_line
    response = json.loads(response_line)
    assert response["id"] == 1
    assert response["result"]["serverInfo"]["name"] == "taskgateway"
    assert process.stderr.read() == ""
