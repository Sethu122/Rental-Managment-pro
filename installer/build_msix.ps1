$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$MakeAppx = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.28000.0\x64\makeappx.exe"
$PackageFolder = Join-Path $ProjectRoot "installer\release\msix-layout"
$MsixPath = Join-Path $ProjectRoot "installer\release\ResidentialRentalManagement.msix"

if (-not (Test-Path -LiteralPath $MakeAppx)) {
  throw "makeappx.exe not found. Install Windows SDK or update the path in installer\build_msix.ps1."
}

Set-Location -Path $ProjectRoot
powershell -ExecutionPolicy Bypass -File ".\installer\prepare_release.ps1"
& $MakeAppx pack /d $PackageFolder /p $MsixPath /overwrite
Write-Host "MSIX package created: $MsixPath"
