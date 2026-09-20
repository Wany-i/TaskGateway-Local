# Runtime directory

This directory is intentionally kept separate from the portable plugin metadata. `install.ps1` creates `venv/` here, installs the released TaskGateway-Local wheel, and copies the WorkBuddy-local index to `index.json`. The MCP command in `.mcp.json` directly spawns `venv/Scripts/python.exe` and imports `taskgateway.mcp_server`; it does not invoke PowerShell, `cmd.exe`, or a shell wrapper.

The directory is empty in the repository so the plugin can be packaged and reviewed without embedding a machine-specific virtual environment. `uninstall.ps1` may remove only this plugin-owned runtime after configuration restoration; it never deletes research archives or source projects.
