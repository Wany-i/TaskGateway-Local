# WorkBuddy installation

The WorkBuddy integration is a local marketplace plugin that bundles a thin skill and one universal STDIO MCP server definition.

## Install from a release checkout

Build or download the `taskgateway_local-<version>-py3-none-any.whl`, then run:

```powershell
cd integrations\workbuddy\plugin
.\install.ps1 `
  -ReleasePackagePath C:\path\to\taskgateway_local-1.0.0-py3-none-any.whl `
  -IndexPath C:\path\to\approved-index.json
```

The installer:

1. creates the local `taskgateway-local` marketplace;
2. backs up WorkBuddy marketplace/settings JSON;
3. enables `task-gateway-local@taskgateway-local`;
4. creates an isolated virtual environment;
5. installs the released package and pinned official MCP SDK;
6. copies the deployment index into plugin runtime data.

Start a fresh WorkBuddy session after installation so plugin MCP configuration is loaded. Use `/mcp` or host logs to confirm the server and all three tools.

Normal tool calls spawn the runtime Python executable directly—no PowerShell or `cmd.exe` wrapper. If a specific host build still creates a visible console, treat that as a failed deployment gate and add a host-only hidden launcher; do not fork the universal MCP server.

## Roll back

Run `uninstall.ps1`. It restores plugin-owned pre-install configuration backups and retains the marketplace files for audit/recovery. Internal research archives are never deleted by the uninstaller.
