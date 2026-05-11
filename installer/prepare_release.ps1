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
The app will ask you to create an administrator account on first launch.
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
Copy-Item -Path "store\Package.appxmanifest" -Destination (Join-Path $MsixLayout "AppxManifest.xml") -Force
New-Item -ItemType Directory -Force -Path (Join-Path $MsixLayout "Assets") | Out-Null
Copy-Item -Path "assets\icons\app.ico" -Destination (Join-Path $MsixLayout "Assets\app.ico") -Force

$AssetScript = @'
from pathlib import Path
from PIL import Image

ico = Path("assets/icons/app.ico")
target = Path("installer/release/msix-layout/Assets")
target.mkdir(parents=True, exist_ok=True)

images = {
    "StoreLogo.png": (50, 50),
    "Square44x44Logo.png": (44, 44),
    "Square150x150Logo.png": (150, 150),
    "Wide310x150Logo.png": (310, 150),
}

source = Image.open(ico).convert("RGBA")
for name, size in images.items():
    canvas = Image.new("RGBA", size, (37, 99, 235, 255))
    image = source.copy()
    image.thumbnail((int(size[0] * 0.72), int(size[1] * 0.72)), Image.LANCZOS)
    x = (size[0] - image.width) // 2
    y = (size[1] - image.height) // 2
    canvas.alpha_composite(image, (x, y))
    canvas.save(target / name)
'@
$AssetScript | python -

Write-Host "Release ZIP: $ZipPath"
Write-Host "MSIX layout folder: $MsixLayout"
