# MCP hosts

TaskGateway-Local is a standards-based local STDIO MCP server. Every compatible host starts the same command:

```text
taskgateway-mcp --index <absolute path to approved index.json>
```

The server exposes:

| Tool | Behavior | Side effect |
|---|---|---|
| `taskgateway_search` | Find eligible indexed resources | None |
| `taskgateway_plan` | Build a route and evaluate the budget | None |
| `taskgateway_invoke` | Validate binding and render a call | None; `executed=false` |

Use an absolute index path because hosts may launch the process from their own working directory. The host owns process lifecycle, user approvals, and any later execution of a rendered command.

## WorkBuddy

Use the plugin in `integrations/workbuddy/plugin`. It registers the server with `${CODEBUDDY_PLUGIN_ROOT}`, creates an isolated runtime, and keeps the deployment index outside the public package.

## Codex

Add a local STDIO MCP server whose command is the installed Python/entry point and whose args contain `--index` plus the absolute approved index path. Codex reads MCP server instructions and tools during initialization.

## Claude and other hosts

Configure the same command under the host's `mcpServers`/local MCP settings. Hosts that do not implement the MCP STDIO client cannot use the server until they add protocol support; no host-specific server fork is required.
