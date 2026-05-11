param(
  [Parameter(Mandatory = $true)]
  [string]$IdentityName,

  [Parameter(Mandatory = $true)]
  [string]$Publisher,

  [Parameter(Mandatory = $true)]
  [string]$PublisherDisplayName,

  [Parameter(Mandatory = $false)]
  [string]$DisplayName = "Residential Rental Management System",

  [Parameter(Mandatory = $false)]
  [string]$Version = "1.0.0.0"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $ProjectRoot "store\Package.appxmanifest"

$manifest = Get-Content -Raw -Path $ManifestPath
$manifest = [regex]::Replace($manifest, 'Name="[^"]+"', "Name=`"$IdentityName`"", 1)
$manifest = [regex]::Replace($manifest, 'Publisher="[^"]+"', "Publisher=`"$Publisher`"", 1)
$manifest = [regex]::Replace($manifest, 'Version="[^"]+"', "Version=`"$Version`"", 1)
$manifest = [regex]::Replace($manifest, '<DisplayName>.*?</DisplayName>', "<DisplayName>$DisplayName</DisplayName>", 1)
$manifest = [regex]::Replace($manifest, '<PublisherDisplayName>.*?</PublisherDisplayName>', "<PublisherDisplayName>$PublisherDisplayName</PublisherDisplayName>", 1)
$manifest = [regex]::Replace($manifest, '<uap:VisualElements DisplayName="[^"]+"', "<uap:VisualElements DisplayName=`"$DisplayName`"", 1)

Set-Content -Path $ManifestPath -Value $manifest -Encoding UTF8
Write-Host "Updated Store manifest identity in $ManifestPath"
