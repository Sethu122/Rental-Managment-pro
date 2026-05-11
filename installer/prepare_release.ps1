$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -Path $ProjectRoot

$AppName = "Residential Rental Management System"
$Version = "1.0.0"
$ReleaseRoot = Join-Path $ProjectRoot "installer\release"
$BundleSource = Join-Path $ProjectRoot "dist\$AppName"
$BundleTarget = Join-Path $ReleaseRoot "$AppName-$Version"
$ZipPath = Join-Path $ReleaseRoot "$AppName-$Version-Windows.zip"
$MsixLayout = Join-Path $ReleaseRoot "msix-layout"

if (-not (Test-Path -LiteralPath $BundleSource)) {
  throw "Build output not found. Run installer\build_exe.ps1 first."
}

if (Test-Path -LiteralPath $ReleaseRoot) {
  Remove-Item -LiteralPath $ReleaseRoot -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $BundleTarget | Out-Null
Copy-Item -Path "$BundleSource\*" -Destination $BundleTarget -Recurse -Force

$Readme = @"
$AppName $Version

To run the application:
1. Open this folder.
2. Double-click "$AppName.exe".

Default first login:
Username: admin
Password: admin123

Change the admin credentials before delivering production copies to clients.
"@
$Readme | Set-Content -Path (Join-Path $BundleTarget "README-FIRST.txt") -Encoding UTF8

for ($attempt = 1; $attempt -le 5; $attempt++) {
  try {
    Compress-Archive -Path "$BundleTarget\*" -DestinationPath $ZipPath -Force
    break
  }
  catch {
    if ($attempt -eq 5) {
      throw
    }
    Start-Sleep -Seconds 3
  }
}

New-Item -ItemType Directory -Force -Path $MsixLayout | Out-Null
Copy-Item -Path "$BundleSource\*" -Destination $MsixLayout -Recurse -Force
Copy-Item -Path "store\Package.appxmanifest" -Destination (Join-Path $MsixLayout "Package.appxmanifest") -Force
New-Item -ItemType Directory -Force -Path (Join-Path $MsixLayout "Assets") | Out-Null
Copy-Item -Path "assets\icons\app.ico" -Destination (Join-Path $MsixLayout "Assets\app.ico") -Force

Write-Host "Release ZIP: $ZipPath"
Write-Host "MSIX layout folder: $MsixLayout"
