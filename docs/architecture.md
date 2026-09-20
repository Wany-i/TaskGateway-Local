# Architecture

TaskGateway-Local separates a dependency-free core from host adapters.

```text
approved index
     |
     v
TaskGateway core
  search -> plan -> invoke (render only)
     |
     +-- Python API
     +-- CLI
     +-- universal STDIO MCP server
              |
              +-- WorkBuddy plugin
              +-- Codex / Claude / other MCP hosts
```

## Core

`taskgateway.core.TaskGateway` loads one explicitly configured index. Search filters disabled and missing resources, scores deterministically, and returns gaps instead of inventing a fallback. Plan produces a bounded route, decision id, and gate decision. Invoke verifies that the decision id is bound to the selected resource and returns a command with `executed: false`.

The core imports no third-party package. The public default index is empty so installation never leaks or assumes a developer machine resource map.

## MCP adapter

`taskgateway.mcp_server` uses the official MCP Python SDK and exposes exactly three structured, read-only tools. It is transport-only: no routing or authorization logic is duplicated. The first release supports STDIO for local hosts; no listener or remote authentication surface is created.

## Trust boundaries

- The index is local deployment data, not public package content.
- Tool results do not grant the host new authority.
- `invoke` never executes its returned command.
- STDOUT belongs exclusively to the MCP protocol.
- Remote transport requires a separate authentication and authorization design and is outside v1.0.0.

## Compatibility

The three tool names, their structured envelopes, and fail-closed behavior are the public compatibility contract. Breaking changes require a new major version.
