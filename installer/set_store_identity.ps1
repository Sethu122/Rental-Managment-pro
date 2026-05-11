param(
  [Parameter(Mandatory = $true)]
  [string]$IdentityName,

  [Parameter(Mandatory = $true)]
  [string]$Publisher,

  [Parameter(Mandatory = $true)]
  [string]$PublisherDisplayName,

  [Parameter(Mandatory = $false)]
  [string]$DisplayName = "Rental Management Pro",

  [Parameter(Mandatory = $false)]
  [string]$Version = "1.0.0.0"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ManifestPath = Join-Path $ProjectRoot "store\Package.appxmanifest"

[xml]$manifest = Get-Content -Raw -Path $ManifestPath
$ns = New-Object System.Xml.XmlNamespaceManager($manifest.NameTable)
$ns.AddNamespace("m", "http://schemas.microsoft.com/appx/manifest/foundation/windows10")
$ns.AddNamespace("uap", "http://schemas.microsoft.com/appx/manifest/uap/windows10")

$identity = $manifest.SelectSingleNode("/m:Package/m:Identity", $ns)
$identity.SetAttribute("Name", $IdentityName)
$identity.SetAttribute("Publisher", $Publisher)
$identity.SetAttribute("Version", $Version)

$manifest.SelectSingleNode("/m:Package/m:Properties/m:DisplayName", $ns).InnerText = $DisplayName
$manifest.SelectSingleNode("/m:Package/m:Properties/m:PublisherDisplayName", $ns).InnerText = $PublisherDisplayName
$manifest.SelectSingleNode("/m:Package/m:Applications/m:Application/uap:VisualElements", $ns).SetAttribute("DisplayName", $DisplayName)

$settings = New-Object System.Xml.XmlWriterSettings
$settings.Encoding = New-Object System.Text.UTF8Encoding($false)
$settings.Indent = $true
$writer = [System.Xml.XmlWriter]::Create($ManifestPath, $settings)
$manifest.Save($writer)
$writer.Close()

Write-Host "Updated Store manifest identity in $ManifestPath"
