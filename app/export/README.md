# Download feature (plug into the main app)

Other teammates own the main UI. This folder is the download path only.

## What it does

After spans exist, the user picks a treatment per field type and downloads a copy.

- keep. Leave it visible.
- blacklabel. Paint it out (text becomes a black bar, photos and signatures become a black plate).
- encrypt. Replace it in the copy and store the original in `vault.enc.json`, locked with a passphrase that is not written into the zip.

Types: name, address, ni_number, account_number, email, phone, date_of_birth, signature, personal_image.

## Python (canonical zip)

From the repo root:

```
.venv\Scripts\python.exe -m app.export --demo --out privacy-gate-export.zip
```

From the main app:

```
from app.export import build_zip_bytes, default_toggles, FIELD_TYPES

zip_bytes, result = build_zip_bytes(
    text=document_text,
    spans=spans,          # [{type, start, end, id?, kind?, image_id?, bbox?}]
    toggles=user_toggles, # {type: "keep"|"blacklabel"|"encrypt"}
    images=images,        # [{id, data_url, alt?}]
    passphrase=phrase_or_none,
    document_name="payslip",
)
```

Serve `zip_bytes` as `application/zip`.

## Drop-in panel

Open `app/static/privacy-export/index.html` in a browser.

Or mount it:

```
PrivacyExport.mount(document.getElementById("slot"), {
  text, spans, images, documentName: "payslip"
});
```

Load `privacy-export.css` and `privacy-export.js` next to your page.
Also load the shared theme first.

```
<link rel="stylesheet" href="/static/theme/tokens.css">
<link rel="stylesheet" href="/static/theme/components.css">
```

Theme files live in `app/static/theme/`. Open `app/static/theme/index.html` to see colour, type, pills, and switches.
