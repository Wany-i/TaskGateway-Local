[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$manifest = Get-Content -Raw (Join-Path $root '.codebuddy-plugin\plugin.json') | ConvertFrom-Json
$mcp = Get-Content -Raw (Join-Path $root '.mcp.json') | ConvertFrom-Json
$skill = Get-Content -Raw (Join-Path $root 'skills\task-gateway-local\SKILL.md')
$readme = Get-Content -Raw (Join-Path $root 'README.md')
$checks = [ordered]@{
    'manifest name/version/license/repository' = ($manifest.name -eq 'task-gateway-local' -and $manifest.version -eq '1.0.0' -and $manifest.license -eq 'MIT' -and $manifest.repository -eq 'https://github.com/wany-i/TaskGateway-Local')
    'stdio MCP server' = ($mcp.mcpServers.'task-gateway-local'.type -eq 'stdio')
    'plugin root interpolation' = ($mcp.mcpServers.'task-gateway-local'.command -like '*${CODEBUDDY_PLUGIN_ROOT}*' -and ($mcp.mcpServers.'task-gateway-local'.args -join ' ') -like '*${CODEBUDDY_PLUGIN_ROOT}*')
    'direct venv Python, no shell' = ($mcp.mcpServers.'task-gateway-local'.command -like '*venv/Scripts/python.exe' -and -not ($mcp.mcpServers.'task-gateway-local'.args -contains 'powershell') -and -not ($mcp.mcpServers.'task-gateway-local'.args -contains 'cmd.exe'))
    'correct MCP module and index' = (($mcp.mcpServers.'task-gateway-local'.args -join ' ') -match 'taskgateway\.mcp_server' -and ($mcp.mcpServers.'task-gateway-local'.args -join ' ') -match 'runtime/index\.json')
    'three tools documented' = (@('search','plan','invoke') | ForEach-Object { $skill -match "\b$_\b" }) -notcontains $false
    'quiet console observation steps' = ($readme -match 'visible command window' -and $readme -match 'stdout' -and $readme -match 'stderr')
}
$failed = @($checks.GetEnumerator() | Where-Object { -not $_.Value })
$checks.GetEnumerator() | ForEach-Object { '{0}: {1}' -f $_.Key, ($(if ($_.Value) { 'PASS' } else { 'FAIL' })) }
if ($failed.Count) { throw "Verification failed: $($failed.Name -join ', ')" }
Write-Host 'Static verification passed; no installation or configuration writes were performed.'
