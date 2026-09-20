[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true)]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
    [string] $ReleasePackagePath,

    [Parameter(Mandatory = $true)]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
    [string] $IndexPath,

    [string] $WorkBuddyRoot = (Join-Path $env:USERPROFILE '.workbuddy'),
    [string] $PythonPath = (Join-Path $env:USERPROFILE '.workbuddy\binaries\python\versions\3.13.12\python.exe'),
    [string] $McpSdkVersion = '2.2.0'
)

$ErrorActionPreference = 'Stop'
$SourcePluginRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$MarketplaceRoot = Join-Path $WorkBuddyRoot 'plugins\marketplaces\taskgateway-local'
$InstalledPluginRoot = Join-Path $MarketplaceRoot 'plugins\task-gateway-local'
$KnownMarketplacesPath = Join-Path $WorkBuddyRoot 'plugins\known_marketplaces.json'
$SettingsPath = Join-Path $WorkBuddyRoot 'settings.json'
$RuntimeRoot = Join-Path $InstalledPluginRoot 'runtime'
$VenvPath = Join-Path $RuntimeRoot 'venv'
$BackupRoot = Join-Path $RuntimeRoot 'config-backups'

function Read-Json([string] $Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return [pscustomobject]@{} }
    return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
}

function Write-AtomicJson([string] $Path, [object] $Value) {
    $parent = Split-Path -Parent $Path
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    $temp = "$Path.$([Guid]::NewGuid().ToString('N')).tmp"
    $Value | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $temp -Encoding UTF8
    Move-Item -LiteralPath $temp -Destination $Path -Force
}

if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) { throw "Python not found: $PythonPath" }
if ([IO.Path]::GetExtension($ReleasePackagePath) -ne '.whl') { throw 'ReleasePackagePath must be a wheel.' }

New-Item -ItemType Directory -Force -Path $InstalledPluginRoot,$RuntimeRoot,$BackupRoot,(Join-Path $MarketplaceRoot '.codebuddy-plugin') | Out-Null
Copy-Item -Path (Join-Path $SourcePluginRoot '*') -Destination $InstalledPluginRoot -Recurse -Force -Exclude 'venv','config-backups'

$marketplace = [ordered]@{
    name = 'taskgateway-local'
    description = 'Local marketplace for the TaskGateway-Local universal MCP plugin.'
    owner = [ordered]@{ name = 'wany-i' }
    metadata = [ordered]@{ version = '1.0.0' }
    plugins = @([ordered]@{
        name = 'task-gateway-local'
        description = 'Universal local TaskGateway search, plan, and invoke MCP tools.'
        source = './plugins/task-gateway-local'
        version = '1.0.0'
        category = 'productivity'
        author = [ordered]@{ name = 'wany-i' }
        repository = 'https://github.com/wany-i/TaskGateway-Local'
        license = 'MIT'
        skills = @('./plugins/task-gateway-local/skills/task-gateway-local')
        mcpServers = './plugins/task-gateway-local/.mcp.json'
    })
}
Write-AtomicJson (Join-Path $MarketplaceRoot '.codebuddy-plugin\marketplace.json') $marketplace

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
foreach ($configPath in @($KnownMarketplacesPath,$SettingsPath)) {
    if (Test-Path -LiteralPath $configPath) {
        Copy-Item -LiteralPath $configPath -Destination (Join-Path $BackupRoot "$(Split-Path -Leaf $configPath).$stamp.bak")
    }
}

$known = Read-Json $KnownMarketplacesPath
$entry = [ordered]@{
    manifestName = 'taskgateway-local'
    type = 'directory'
    source = [ordered]@{ source = 'directory'; path = $MarketplaceRoot }
    installLocation = $MarketplaceRoot
    description = "Marketplace from $MarketplaceRoot"
    lastUpdated = (Get-Date).ToUniversalTime().ToString('o')
    autoUpdate = $false
}
$known | Add-Member -NotePropertyName 'taskgateway-local' -NotePropertyValue $entry -Force
Write-AtomicJson $KnownMarketplacesPath $known

$settings = Read-Json $SettingsPath
if (-not ($settings.PSObject.Properties.Name -contains 'enabledPlugins')) {
    $settings | Add-Member -NotePropertyName enabledPlugins -NotePropertyValue ([pscustomobject]@{})
}
$settings.enabledPlugins | Add-Member -NotePropertyName 'task-gateway-local@taskgateway-local' -NotePropertyValue $true -Force
Write-AtomicJson $SettingsPath $settings

if (-not (Test-Path -LiteralPath $VenvPath)) { & $PythonPath -m venv $VenvPath }
$RuntimePython = Join-Path $VenvPath 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $RuntimePython)) { throw "Virtualenv Python missing: $RuntimePython" }
& $RuntimePython -m pip install --disable-pip-version-check --no-input "mcp==$McpSdkVersion" $ReleasePackagePath
Copy-Item -LiteralPath $IndexPath -Destination (Join-Path $RuntimeRoot 'index.json') -Force

& (Join-Path $InstalledPluginRoot 'verify.ps1')
Write-Host "Installed task-gateway-local at $InstalledPluginRoot. Start a fresh WorkBuddy session to load its MCP server."
