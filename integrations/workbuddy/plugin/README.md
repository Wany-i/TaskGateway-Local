# task-gateway-local WorkBuddy plugin

Portable CodeBuddy/WorkBuddy plugin for [TaskGateway-Local](https://github.com/wany-i/TaskGateway-Local), version `1.0.0`, licensed MIT.

It registers one stdio MCP server with three tools: `search`, `plan`, and `invoke`. The server is started by spawning the plugin-owned virtualenv Python directly through `${CODEBUDDY_PLUGIN_ROOT}`. No shell or visible command window is used for ordinary MCP calls.

## Install (not performed by this package build)

Run from this directory in an elevated or appropriately permissioned PowerShell session:

```powershell
.\install.ps1 `
  -ReleasePackagePath C:\path\to\TaskGateway-Local\dist\taskgateway_local-1.0.0-py3-none-any.whl `
  -IndexPath C:\path\to\workbuddy-index.json
```

The installer targets the local-directory marketplace named `taskgateway-local`, backs up `known_marketplaces.json` and `settings.json`, writes each update atomically, creates `runtime\venv`, and installs the supplied local release package plus the pinned MCP SDK. It does not install from PyPI or reach into `.workbuddy`.

The release package must expose `taskgateway.mcp_server` and the three MCP tools listed above. The installer pins the official Python MCP SDK to `2.2.0`; changing that pin is reserved for deliberate compatibility validation.

## Remove

```powershell
.\uninstall.ps1
```

Uninstall restores the most recent plugin-owned configuration backup when present and removes only the plugin-owned marketplace entry and runtime. It preserves research archives, source projects, and unrelated marketplace entries. Use `-KeepRuntime` to retain the venv for inspection.

## Verify without installing

```powershell
.\verify.ps1
```

Verification is static and safe: it checks the manifest, stdio MCP config, skill, all three tool names, `${CODEBUDDY_PLUGIN_ROOT}`, direct venv Python spawning, and the no-visible-console observation steps. It does not create a venv, edit configuration, or start the MCP server.

## Runtime contract

The server emits MCP protocol traffic on stdout and diagnostics only on stderr. `invoke` is a renderer, not an executor: it returns `executed: false` and callers must honor the gate and side-effect budget.
