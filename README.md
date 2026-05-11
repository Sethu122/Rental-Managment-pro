# Rental-Managment-pro

Residential Rental Management System is a commercial Windows desktop application for managing residential rental properties, units, tenants, rent arrears, maintenance, and reports.

## Features

- Local authentication with PBKDF2 password hashing.
- Offline SQLite database with automatic first-launch schema creation.
- Property and unit management.
- Tenant management with unit assignment, monthly rent, and lease dates.
- Rent tracking with paid/unpaid status, automatic rent periods, arrears, and outstanding balance.
- Maintenance issue tracking by unit with Pending, In Progress, and Completed states.
- Dashboard for total properties, tenants, arrears, and open maintenance.
- Rent summary PDF export and CSV export.
- White-label branding via `config/branding.json`.
- Local license validation with trial mode and property-count limits.
- PyInstaller Windows packaging with no console window.
- Microsoft Store MSIX preparation files and publishing guide.

## First Launch

On first launch, the app opens a setup screen and requires the customer to create a local administrator account. No default credentials are shipped.

## Development Setup

```powershell
cd "C:\Users\user\Documents\New project\rental_app"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Branding

Edit `config/branding.json`:

```json
{
  "app_name": "Residential Rental Management System",
  "company_name": "Your Property Company",
  "logo": "assets/logos/logo.png",
  "primary_color": "#2563EB"
}
```

## Licensing

The app runs in `TRIAL` mode without a valid local license. Trial mode limits the number of properties.

Production license keys are validated locally by `app/services/license_service.py`. Generate client keys with `LicenseService.expected_key(licensed_to, expires_at)` and store the issued client/company name and expiry date with the key.

## Build Windows EXE

```powershell
cd "C:\Users\user\Documents\New project\rental_app"
.\installer\build_exe.ps1
```

The executable is created under:

- `dist/Residential Rental Management System/`
- `installer/output/Residential Rental Management System.exe`

## Prepare Release Package

```powershell
.\installer\prepare_release.ps1
```

This creates:

- `installer/release/Residential Rental Management System-1.0.0-Windows.zip`
- `installer/release/msix-layout/`

## Optional Inno Setup Installer

Install Inno Setup, then compile:

```powershell
iscc .\installer\ResidentialRentalManagement.iss
```

## Microsoft Store

See `store/MSIX_PUBLISHING_GUIDE.md` and `store/Package.appxmanifest`.

## Data Storage

The SQLite database is created locally as `rental_management.db` beside the executable during packaged execution, or in the project root during development.

## License

Proprietary commercial software. See `LICENSE.txt`.
