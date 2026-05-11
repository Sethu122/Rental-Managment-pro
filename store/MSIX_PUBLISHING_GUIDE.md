# Microsoft Store MSIX Publishing Guide

1. Reserve the app name in Partner Center: **Residential Rental Management System**.
2. Replace the manifest identity in `store/Package.appxmanifest`:
   - `Identity Name`
   - `Publisher`
   - `PublisherDisplayName`
   - `Version`
3. Build the PyInstaller executable with `installer/build_exe.ps1`.
4. Create MSIX layout:
   - Copy the contents of `dist/Residential Rental Management System/` into a clean package folder.
   - Copy `store/Package.appxmanifest` into that package folder.
   - Add Store logo PNG assets under `Assets/`.
5. Package with Windows SDK tools:
   - `makeappx pack /d <PackageFolder> /p ResidentialRentalManagement.msix`
6. Sign the MSIX:
   - For local testing, create a test cert with `New-SelfSignedCertificate`.
   - For Store upload, use the identity and signing process provided by Partner Center.
   - `signtool sign /fd SHA256 /a /f <cert.pfx> ResidentialRentalManagement.msix`
7. Validate before submission:
   - Run Windows App Certification Kit.
   - Confirm no console window appears.
   - Confirm offline SQLite storage works.
   - Confirm trial mode and license activation work.
   - Confirm PDF/CSV export uses user-selected save locations.
8. Upload the `.msix` package to Partner Center, complete pricing, age rating, privacy policy, screenshots, description, and certification notes.
