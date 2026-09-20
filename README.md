# TaskGateway-Local

TaskGateway-Local is a deterministic, fail-closed gateway for discovering approved local resources, planning a bounded route, and rendering—but never executing—a selected call.

It exposes the same three operations through Python, a CLI, and a universal local MCP server:

- `taskgateway_search`
- `taskgateway_plan`
- `taskgateway_invoke`

`invoke` always returns `executed: false`. The host retains its normal authorization and execution boundary.

## Install

From the v1.0.0 GitHub release:

```powershell
python -m pip install https://github.com/wany-i/TaskGateway-Local/releases/download/v1.0.0/taskgateway_local-1.0.0-py3-none-any.whl
```

For development, or when the MCP extra must be resolved explicitly:

```powershell
git clone https://github.com/wany-i/TaskGateway-Local.git
cd TaskGateway-Local
python -m pip install ".[mcp]"
```

Python 3.11–3.13 is supported. An approved local index must be provided explicitly; the public package does not ship a private machine index.

## CLI

```powershell
taskgateway search "find an approved resource" --index C:\path\to\index.json --json
taskgateway plan "read an approved resource" --index C:\path\to\index.json --json
taskgateway invoke "<resource_ref>" --decision-id "<decision_id>" --index C:\path\to\index.json --json
```

## MCP

Start the universal STDIO server:

```powershell
taskgateway-mcp --index C:\path\to\index.json
```

The host launches this process and communicates over stdin/stdout. No port is opened. STDOUT is reserved for MCP protocol messages; application logging belongs on stderr.

WorkBuddy packaging is under `integrations/workbuddy/plugin/`. Other MCP hosts use the same server command; see [MCP hosts](docs/mcp-hosts.md).

## Verify

```powershell
python -m pip install -e ".[mcp,test]"
python -m pytest -q
```

The test suite covers core fail-closed behavior, tool schemas and annotations, structured MCP output, and a real STDIO initialization handshake.

## Documentation

- [Architecture](docs/architecture.md)
- [WorkBuddy installation](docs/workbuddy-install.md)
- [MCP hosts](docs/mcp-hosts.md)
- [Maintenance and releases](docs/maintenance.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## License

Released under the [MIT License](LICENSE).
