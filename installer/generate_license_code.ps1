param(
  [Parameter(Mandatory = $true)]
  [string]$LicensedTo,

  [Parameter(Mandatory = $true)]
  [string]$ExpiresAt
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -Path $ProjectRoot

$script = @"
from app.services.license_service import LicenseService
print(LicenseService().generate_license_token("$($LicensedTo.Replace('"', '\"'))", "$ExpiresAt"))
"@

$script | python -
