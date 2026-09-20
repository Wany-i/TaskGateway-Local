---
name: task-gateway-local
description: Use the local TaskGateway-Local MCP server to discover resources, build a gated read-only route, and render a safe invocation command.
---

# TaskGateway-Local

Use the `task-gateway-local` MCP server for local resource discovery and routing. It provides three tools:

- `search`: deterministic, read-only resource search. Start here when the user asks where a skill, tool, connector, standard, or library lives.
- `plan`: produce a three-step route (`read_norms`, `inspect`, `invoke_if_allowed`) and evaluate the requested side-effect budget.
- `invoke`: render, but do not execute, a command bound to a valid `decision_id`. It is fail-closed and requires the resource reference from `search`/`plan`.

Normal flow: call `search`, call `plan` for an actionable goal, then call `invoke` only with the returned resource reference and decision ID. Treat `blocked`, `NO_ELIGIBLE_RESOURCE`, `DECISION_UNKNOWN`, `PATH_MISSING`, and `GATE_DENIED` as stop conditions. Do not bypass the gate by opening local files, shelling out, or inventing a decision ID.

The server is local-only and communicates over stdio. The MCP process must remain quiet on stdout except for protocol messages; diagnostics belong on stderr. `invoke` intentionally returns `executed: false`: the host or operator remains responsible for any side effect.

## Input guidance

- Keep `query`/`goal` specific and include the user’s domain terms.
- Use `read_only` unless the user explicitly authorizes a bounded write or execute budget.
- Preserve the complete response envelope in follow-up reasoning, especially `gaps`, `warnings`, `gate`, and `next_action`.

## Installation boundary

The installer creates an isolated `runtime/venv` and installs the local TaskGateway-Local release package plus a pinned MCP SDK. It does not copy or mutate the user’s `.workbuddy` archive or any project on `D:`. The package is usable only after the installer has been run by the user.
