$ErrorActionPreference = "Stop"
Set-Location -Path (Split-Path -Parent $PSScriptRoot)

python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean `
  --name "Residential Rental Management System" `
  --windowed `
  --icon "assets/icons/app.ico" `
  --add-data "config;config" `
  --add-data "assets;assets" `
  main.py

if (Test-Path -LiteralPath "installer/output") {
  Remove-Item -LiteralPath "installer/output" -Recurse -Force
}
New-Item -ItemType Directory -Force -Path "installer/output" | Out-Null
Copy-Item -Path "dist/Residential Rental Management System/*" -Destination "installer/output" -Recurse -Force
Write-Host "Executable bundle created in dist/Residential Rental Management System and copied to installer/output."
