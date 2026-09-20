[CmdletBinding()]
param([string] $WorkBuddyRoot = (Join-Path $env:USERPROFILE '.workbuddy'))

$ErrorActionPreference = 'Stop'
$MarketplaceRoot = Join-Path $WorkBuddyRoot 'plugins\marketplaces\taskgateway-local'
$InstalledPluginRoot = Join-Path $MarketplaceRoot 'plugins\task-gateway-local'
$KnownPath = Join-Path $WorkBuddyRoot 'plugins\known_marketplaces.json'
$SettingsPath = Join-Path $WorkBuddyRoot 'settings.json'
$BackupRoot = Join-Path $InstalledPluginRoot 'runtime\config-backups'

function Restore-Latest([string] $Path) {
    if (-not (Test-Path -LiteralPath $BackupRoot)) { return $false }
    $leaf = Split-Path -Leaf $Path
    $backup = Get-ChildItem -LiteralPath $BackupRoot -Filter "$leaf.*.bak" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($null -eq $backup) { return $false }
    Copy-Item -LiteralPath $backup.FullName -Destination $Path -Force
    return $true
}

$knownRestored = Restore-Latest $KnownPath
$settingsRestored = Restore-Latest $SettingsPath
if (-not $knownRestored -or -not $settingsRestored) {
    throw 'A plugin-owned configuration backup is missing; no partial uninstall was performed.'
}
Write-Host "Plugin configuration disabled by restoring pre-install settings. Files remain at $MarketplaceRoot for audit/recovery."
