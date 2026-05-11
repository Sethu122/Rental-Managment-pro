# Partner Center Publishing Checklist

## Values Required From Partner Center

Copy these from the app reservation/package identity page:

- Package/Identity Name
- Publisher
- Publisher display name
- Reserved app name

Apply them locally with:

```powershell
.\installer\set_store_identity.ps1 `
  -IdentityName "PASTE_PACKAGE_IDENTITY_NAME" `
  -Publisher "PASTE_PUBLISHER_VALUE" `
  -PublisherDisplayName "PASTE_PUBLISHER_DISPLAY_NAME" `
  -DisplayName "Residential Rental Management System" `
  -Version "1.0.0.0"
```

Then rebuild:

```powershell
.\installer\build_exe.ps1
.\installer\build_msix.ps1
```

Upload this file in Partner Center:

```text
installer\release\ResidentialRentalManagement.msix
```

## Store Submission Fields

- Price: choose the closest paid tier to USD 250.
- Category: Business.
- Support contact: add your real support email or website.
- Privacy policy: add a public URL. The draft text is in `store/STORE_LISTING_DRAFT.md`.
- Certification notes: include the note from `store/STORE_LISTING_DRAFT.md`.

## Final Checks Before Submit

- App launches without a console window.
- First launch creates an administrator account.
- App works offline.
- PDF export works.
- CSV export works.
- No development database is included in the MSIX.
- Package identity matches Partner Center exactly.
