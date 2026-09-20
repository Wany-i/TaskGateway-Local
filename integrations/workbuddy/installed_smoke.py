"""Smoke-test an installed TaskGateway MCP server over real STDIO."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def send(process: subprocess.Popen[str], payload: dict) -> dict:
    assert process.stdin and process.stdout
    process.stdin.write(json.dumps(payload) + "\n")
    process.stdin.flush()
    line = process.stdout.readline()
    if not line:
        raise RuntimeError("MCP server closed stdout before responding")
    return json.loads(line)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    args = parser.parse_args()
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    process = subprocess.Popen(
        [
            str(args.python),
            "-m",
            "taskgateway.mcp_server",
            "--index",
            str(args.index),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=flags,
    )
    try:
        initialized = send(
            process,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "workbuddy-smoke", "version": "1.0"},
                },
            },
        )
        send_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }
        assert process.stdin
        process.stdin.write(json.dumps(send_notification) + "\n")
        process.stdin.flush()
        tools = send(
            process,
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        )
        names = {tool["name"] for tool in tools["result"]["tools"]}
        expected = {
            "taskgateway_search",
            "taskgateway_plan",
            "taskgateway_invoke",
        }
        if names != expected:
            raise RuntimeError(f"unexpected tools: {sorted(names)}")
        search = send(
            process,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "taskgateway_search",
                    "arguments": {"query": "查找资料库中的交接文档", "limit": 3},
                },
            },
        )
        if search.get("error"):
            raise RuntimeError(search["error"])
        print(
            json.dumps(
                {
                    "server": initialized["result"]["serverInfo"],
                    "tools": sorted(names),
                    "search_call": "PASS",
                    "visible_console": False,
                },
                ensure_ascii=False,
            )
        )
        return 0
    finally:
        process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
