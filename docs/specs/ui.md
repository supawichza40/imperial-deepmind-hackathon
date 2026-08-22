# Privacy Gate — UI spec (backend contract)

**What this is:** the frontend the demo actually runs. Backend should implement against this file, not against the Streamlit design in [design.md](design.md).
**Status:** live in `app/static/` as of commit `50d340c` (22 Aug 2026). FastAPI is specified in [api.md](api.md) but is not wired yet. The browser currently holds vault state in `localStorage` and runs redaction, QR pack, TOTP, and folder locks locally.
**Audience:** whoever is writing the FastAPI layer, detector, and Gemini call.
**How to open it:** serve `app/static` over HTTP, then hit the routes in §2.

```
.venv/Scripts/python.exe -m http.server 8765 --directory app/static
```

Vault: http://127.0.0.1:8765/vault/
Export panel: http://127.0.0.1:8765/privacy-export/
Theme: http://127.0.0.1:8765/theme/

---

## 1. Product job

Privacy Gate is assisted redaction with human approval. It is not guaranteed anonymisation.

The user reviews a synthetic payslip, chooses a treatment per field type, and only the sanitised copy can leave the device. A second phone can receive that copy by scanning a QR. The original never goes in the QR and never goes to Gemini.

Two layers the backend must keep apart:

| Layer | Who sees original text | Who sees sanitised text |
|---|---|---|
| Local (Gemma / regex, vault, export) | yes | yes |
| Cloud (Gemini 3.7 Flash) | never | yes, after consent |
| QR / share guest | never | yes, optionally AES-GCM locked with a creator key |

---

## 2. Live routes (static today, FastAPI tomorrow)

Serve these exact paths. Do not invent a single `static/index.html` SPA until the vault and export mounts still work.

| Path | File | Job |
|---|---|---|
| `/vault/` or `/vault/index.html` | `app/static/vault/index.html` | Folders, ACL, lock, two-step delete, share QR, guest open |
| `/privacy-export/` | `app/static/privacy-export/index.html` | Standalone consent + download panel |
| `/theme/` | `app/static/theme/index.html` | Token playground. Not a product screen |

Scripts the vault page loads, in this order:

1. `theme/tokens.js`
2. `privacy-export/privacy-export.js`
3. `privacy-export/demo-payload.js`
4. `vault/qrcodegen.js` (Nayuki, MIT, versions 1–40)
5. `vault/qr.js` (`PrivacyQr.svg`)
6. `vault/vault.js` (`PrivacyVault.mount`)

Styles: `theme/tokens.css`, `theme/components.css`, `privacy-export/privacy-export.css`, `vault/vault.css`.

Hash routes on the vault page:

| Hash | Meaning |
|---|---|
| `#t=<payload>` | Instant transfer. Gzip JSON of the sanitised file is inside the URL. Works on another phone. |
| `#s=<id-or-token>` | Old signed pointer. Needs this browser's `localStorage` HMAC secret. Do not use this for the demo QR. |

---

## 3. Screen map

Target product flow is in `docs/visual/2026-08-22-privacy-gate-screens.html`. Built modules cover S4/S5 plus vault. S1–S3 and S6–S8 are still for the main app to wire.

| ID | Screen | Built? | What the user does | What backend must supply |
|---|---|---|---|---|
| S1 | Drop a document | mock only | Click the sample payslip. No live file upload. | `GET /api/documents` with the synthetic payslip (and bank statement if you build FR-3). |
| S2 | Reading it | not built | Short local wait. Copy says nothing left the machine. | No request yet. |
| S3 | Finding private fields | not built in UI | Gemma + regex highlight spans. Wifi-off still works. | `POST /api/detect`. Span shape in §6. Timeout 3s then regex-only + warning. |
| S4 | Review and approve | **live** `PrivacyExport` | Per-type toggle. Keep / blacklabel / encrypt. | Feed `{text, spans, images}` into the panel. Do not replace this widget. |
| S5 | Exactly what leaves | **live** preview + download | User sees the sanitised copy before anything is sent or shared. | Same panel. Optional `POST /api/export-zip` if you want the Python zip instead of browser HTML/txt. |
| S6 | Thinking | not built | Cloud wait. Keep the sanitised payload on screen. | `POST /api/reason` with sanitised text only. |
| S7 | What it found | not built | One concrete mismatch (net pay £2,427.40 vs deposit £2,480.00). | Gemini JSON in §6.5. |
| S8 | The receipt | partial | Export already writes `audit.json`. Vault does not yet show a cloud receipt. | `POST /api/audit` plus display. Never cut this from the demo. |
| Vault | Folders + share | **live** | Grant roles, lock, delete, mint QR. | Optional persist. Python `app.access.Vault` already matches the rules. |
| Guest | Open QR | **live** | Phone shows sanitised text. Optional creator key. | `unpack_file` if you verify payloads server-side. Not required for the QR path. |
| E1 | Local model down | not built | Regex fallback + warning. | Detector returns `fallback_triggered`. |
| E2 | Nothing found | not built | Manual types still listed, disabled if absent. | Empty `spans` is valid. Panel already handles "not in this document". |
| E3 | Cloud failed | not built | Show a saved example. Return 200 with fallback body, not 502. | See [api.md](api.md) §2.4. |

Demo order that already works without FastAPI:

1. Open vault.
2. Flip privacy toggles on the payslip (S4).
3. Watch the preview (S5).
4. Share file → Make link and QR.
5. Scan on a phone on the same WiFi (`#t=`).

Wire S1→S3 and S6→S8 on top of this. Do not rebuild S4/S5.

---

## 4. Theme (do not fork)

Framery-inspired mist / paper / wood. Tokens live in `app/static/theme/tokens.css`.

| Token | Hex | Use |
|---|---|---|
| `--theme-mist` | `#f7f5f2` | Page background |
| `--theme-paper` | `#ffffff` | Cards |
| `--theme-sand` | `#f4f1ea` | Local / keep wash |
| `--theme-ink` | `#111111` | Text, primary buttons, QR modules, blacklabel |
| `--theme-mute` | `#666666` | Secondary copy |
| `--theme-line` | `#e6e1d8` | Borders |
| `--theme-wood` | `#c4a574` | Encrypt accent |
| `--theme-wood-deep` | `#8c6a3c` | Wood text |
| `--theme-danger` | `#8a2a22` | Errors, delete |

Type: Inter. Buttons are stadium pills, 11px, 0.16em tracking, uppercase. Cards 28px radius. Inputs 16px radius. Page max 1120px.

Respect `prefers-reduced-motion` (`--theme-fast` becomes `0ms`).

Copy voice: short, specific, no slogans. Say "assisted redaction with human approval". Never say the product anonymises.

---

## 5. Frontend modules (keep these APIs)

### 5.1 `PrivacyExport.mount(el, opts)`

`app/static/privacy-export/privacy-export.js`

```js
PrivacyExport.mount(slot, {
  text: String,          // full document
  spans: Array<Span>,    // §6.1
  images: Array<Image>,  // §6.2
  documentName: String,  // download stem, e.g. "payslip"
  toggles: Object        // optional { type: "keep"|"blacklabel"|"encrypt" }
});
```

Returns `{ getToggles(), getResult() }`. After paint, the element stores:

- `el._result = { text, audit, html }`
- `el._toggles = { ... }`

Vault share reads `el._result.text` as the QR body. If the detector later feeds live spans, mount with those instead of `window.PRIVACY_EXPORT_DEMO`.

Demo payload: `app/static/privacy-export/demo-payload.js` → `window.PRIVACY_EXPORT_DEMO`.

Buttons the vault already clicks by id:

| Id | Action |
|---|---|
| `#pg-html` | Download sanitised HTML. If any type is encrypt, also require passphrase and download `*-vault-meta.json`. |
| `#pg-txt` | Download sanitised `.txt` |
| `#pg-json` | Download `{ toggles, audit }` |
| `#pg-share` | If not on `/vault/`, send the browser to `/vault/`. If on vault, clicks `#btn-share`. If that button is disabled, show an error. |
| `#pg-pass` | Passphrase. Shown only when a type is encrypt. Never written into the HTML. |

### 5.2 `PrivacyVault.mount(el, { email })`

`app/static/vault/vault.js`

Default actor `you@local`. State key `localStorage["pg-vault-v1"]`.

Seed:

- Folders: Inbox, Identity, Shared (all owned by the actor).
- One doc: `{ name: "July payslip", kind: "payslip" }` in Inbox.
- TOTP secret (base32) and a 32-byte HMAC secret, both generated in the browser.

When FastAPI owns the vault, replace `load`/`save` with REST. Keep the same role names, delete ritual, and share modal.

### 5.3 `PrivacyQr.svg(url)`

Returns an SVG string, or `""` if the URL will not fit a version 40 code at ECC LOW. Keep packed `#t=` URLs under **2900 bytes** UTF-8. Tests assert this for a blacklabeled sample payslip.

---

## 6. Data contracts the UI already consumes

Backend JSON must match these names. Extra keys are ignored. Missing keys break the panel.

### 6.1 Span

Zero-based Python offsets. `end` exclusive. `text[start:end]` must equal `value` when `end > start`.

```json
{
  "id": "name-1",
  "type": "name",
  "start": 50,
  "end": 59,
  "value": "A. Okafor",
  "kind": "text"
}
```

Image / signature spans use `start: 0`, `end: 0` and point at an image:

```json
{
  "id": "photo-1",
  "type": "personal_image",
  "start": 0,
  "end": 0,
  "kind": "personal_image",
  "image_id": "staff-photo",
  "bbox": [0.32, 0.18, 0.36, 0.55]
}
```

`bbox` is `[x, y, w, h]` in 0–1 fractions of the image. Used when the whole photo is kept but a region is labelled.

Unknown `type` values still appear as extra toggles (`label_for` title-cases the id).

### 6.2 Image

```json
{
  "id": "staff-photo",
  "alt": "Staff photo",
  "data_url": "data:image/svg+xml;utf8,..."
}
```

Special ids the panel treats as whole-object hide:

- `staff-photo` follows toggle `personal_image`
- `wet-signature` follows toggle `signature`

### 6.3 Field types and default toggles

Canonical list in `app/export/fields.py` and the JS panel. **Nine types**, not the five in the old requirements spec.

| `type` | Label | Default |
|---|---|---|
| `name` | Name | blacklabel |
| `address` | Address | blacklabel |
| `ni_number` | NI number | blacklabel |
| `account_number` | Account number | blacklabel |
| `email` | Email | blacklabel |
| `phone` | Phone | blacklabel |
| `date_of_birth` | Date of birth | blacklabel |
| `signature` | Signature | blacklabel |
| `personal_image` | Personal photo | blacklabel |

Pay figures (`Gross pay`, `Net pay`, etc.) are **not** a field type. They stay visible unless you add a new type such as `income`. If you add `income`, default it to `keep` so the Gemini mismatch still shows.

Toggle values (per type, not per span):

| Value | Text treatment | Photo / signature |
|---|---|---|
| `keep` | unchanged, green mark | shown |
| `blacklabel` | block of `█` same length, or `[BLACKLABELED NAME]` in some Python paths | black plate, original omitted from zip |
| `encrypt` | `[ENCRYPTED NAME]` | encrypted blob, passphrase not in the file |

Do **not** emit `[REDACTED]` if this UI is the consumer. The live panel and `app.export.redact` use the table above.

A type with no spans in the document still shows in the list, checkbox disabled, hint "not in this document".

### 6.4 Detect response the panel needs

When you build `POST /api/detect`, return this so the frontend can call `PrivacyExport.mount` without reshaping:

```json
{
  "results": {
    "payslip": {
      "text": "ACME LTD  —  PAYSLIP\n...",
      "spans": [ { "id": "...", "type": "name", "start": 50, "end": 59, "value": "A. Okafor", "kind": "text" } ],
      "images": [ { "id": "staff-photo", "alt": "Staff photo", "data_url": "data:..." } ],
      "documentName": "payslip",
      "fallback_triggered": false,
      "warning": ""
    }
  }
}
```

`text` is required here even though [api.md](api.md) currently omits it. The panel cannot highlight without the same string the offsets were measured on.

### 6.5 Gemini result (S7)

Unchanged from the requirements spec. UI has no renderer yet.

```json
{
  "inconsistency_detected": true,
  "analysis": "The payslip shows net pay of £2,427.40, but the bank deposit is £2,480.00. Difference £52.60.",
  "draft_letter": "Dear Pelham Consulting, ..."
}
```

Send **only** `sanitised_payload` (the string from `PrivacyExport` result text, or concatenated multi-doc payload). Never send `spans.value`, never send original `text`.

### 6.6 Consent object (if you keep POST /api/sanitise)

The old API used `shared_types` / `blocked_types`. The live UI uses three actions. Prefer:

```json
{
  "toggles": {
    "name": "blacklabel",
    "address": "blacklabel",
    "ni_number": "blacklabel",
    "account_number": "blacklabel",
    "email": "blacklabel",
    "phone": "blacklabel",
    "date_of_birth": "blacklabel",
    "signature": "blacklabel",
    "personal_image": "blacklabel"
  },
  "passphrase": null
}
```

`passphrase` is required when any value is `encrypt`. Whitespace-only is rejected. It must never be logged or echoed.

Map to the old shape only if you must: `keep` → shared, `blacklabel` or `encrypt` → blocked. That loses encrypt and is not what the panel shows.

### 6.7 Audit entry the download already writes

Browser `#pg-json` writes:

```json
{
  "toggles": { "name": "blacklabel" },
  "audit": [
    { "id": "name-1", "type": "name", "action": "blacklabel", "replacement": "█████████" }
  ]
}
```

Python zip also writes `toggles.json` and `audit.json`. Cloud receipt (S8) can add `kept_local` / `shared` / `fallback` rows from [privacy-gate.md](privacy-gate.md) §3.8. Show both: field treatments, then what crossed to Gemini.

---

## 7. Vault, ACL, lock, delete

Python source of truth: `app/access/` (`Vault`, `Acl`, `share.py`, `totp.py`). JS mirrors it for the demo.

### 7.1 Roles (strongest last)

`viewer` < `downloader` < `editor` < `admin` < `owner`

| Action | Minimum role |
|---|---|
| view | viewer |
| download | downloader |
| share | editor |
| write (new folder / doc) | editor |
| acl (grant / revoke) | admin |
| lock | admin |
| delete | owner |

Owner cannot be granted or removed. Grant roles are only `viewer`, `downloader`, `editor`, `admin`.

Child folder: inherit parent members, child wins on the same email. If parent owner ≠ child owner, parent owner is at least `admin` on the child.

Check ACL at action time, not only at grant time.

### 7.2 Folder lock

PBKDF2-HMAC-SHA256, **210000** rounds, 16-byte salt, 32-byte hash. JS stores salt/hash as urlsafe base64 without padding.

Locked + not unlocked: hide docs, disable Download and Share. Unlock needs the passphrase. Parent lock also blocks child write/list.

Empty passphrase is rejected.

### 7.3 Two-step delete

1. Typed folder name must match exactly (after strip).
2. 6-digit TOTP, SHA-1, 30-second steps, window includes previous step.

Deletes the folder and all descendant folders and their docs.

### 7.4 Suggested vault endpoints (not built)

Mirror `app.access.Vault` if you persist server-side. Actor identity can stay `you@local` for the hackathon.

| Method | Path | Body / notes |
|---|---|---|
| GET | `/api/vault` | `{ email, folders, docs }` no TOTP secret in JSON if you can avoid it. Demo currently shows a live code. |
| POST | `/api/vault/folders` | `{ name, parent_id }` |
| POST | `/api/vault/folders/{id}/grant` | `{ email, role }` |
| POST | `/api/vault/folders/{id}/lock` | `{ passphrase }` |
| POST | `/api/vault/folders/{id}/unlock` | `{ passphrase }` |
| POST | `/api/vault/folders/{id}/delete` | `{ typed_name, totp_code }` |
| GET | `/api/vault/folders/{id}/docs` | 403 if locked |
| POST | `/api/vault/docs/{id}/share` | `{ perm, ttl_seconds, require_key }` → see §8 |

Until these exist, do not break the localStorage vault. Same-origin static files are enough for the share QR demo.

---

## 8. Share and QR

Two pack formats exist. **Use `#t=` for any phone.** `#s=` is a leftover that only works in the same browser that minted it.

### 8.1 Instant transfer (`#t=`) — required for demo

Python: `app.access.transfer.pack_file` / `unpack_file`.
JS: `packTransfer` / `unpackTransfer` in `vault.js`.

URL:

```
http://<lan-ip>:8765/vault/index.html#t=<urlsafe-b64-gzip-json>
```

If the page is opened as `127.0.0.1` or `localhost`, the vault tries WebRTC ICE to swap in a private IPv4 (`10/8`, `192.168/16`, `172.16–31`) so a phone is not sent to loopback. If that fails, the UI tells the user to open the vault as the WiFi IP first.

**Unkeyed JSON** (then gzip, then urlsafe b64, no padding):

```json
{ "v": 1, "n": "July payslip", "p": "download", "x": 1755870000, "t": "<sanitised text>" }
```

**Keyed JSON** (`require_key` / "Ask for my key"):

```json
{
  "v": 1,
  "x": 1755870000,
  "k": 1,
  "s": "<urlsafe salt>",
  "i": "<urlsafe nonce>",
  "c": "<urlsafe ciphertext>"
}
```

Inner plaintext (AES-GCM, then json): `{ "n", "p", "t" }`.

Rules:

- `p` is `view` or `download` only.
- `x` is unix expiry. UI offers 3600 or 86400 seconds.
- Creator key is **not** in the URL. Format `XXXX-XXXX`. Alphabet `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` (no O, I, 0, 1). Compare after `normalize_key`: uppercase, alnum only.
- AES-GCM 256. PBKDF2-HMAC-SHA256, 210000 rounds, salt 16 bytes, nonce 12 bytes. Passphrase for KDF is `normalize_key(creator_key)`.
- Keyed packs with the same inputs must not be identical (fresh salt/nonce).
- Incomplete JSON (missing `n`/`p`/`t` on an unkeyed pack) → `ValueError("bad transfer payload")`.
- Guest UI for `#t=`: read-only `<pre class="pg-transfer-doc">`. Not the payslip export panel. Download button only if `p === "download"`.
- If `k` is set and no key typed: screen "This file needs the creator's key".

### 8.2 Signed pointer (`#s=`) — same machine only

HMAC-SHA256 over urlsafe body. Body fields: `f` folder id, `d` doc id, `p` perm, `by` actor, `exp`, optional `kh` (first 16 bytes of HMAC of `pg-key:` + normalized key, urlsafe).

Python: `app.access.share.mint_with_key` / `open_token`. Needs the vault HMAC secret. A second phone does not have it. Keep for in-browser tests. Do not put this in the QR.

### 8.3 Encrypt passphrase vs creator key

These are different secrets. Do not mix them.

| Secret | Who types it | Where it lives |
|---|---|---|
| Export passphrase | downloader, when a type is encrypt | never in zip, HTML, QR, or share token |
| Creator key | guest opening a keyed `#t=` | shown once to the creator in the share modal |
| Folder lock | folder admin | PBKDF2 hash on the folder |
| TOTP | owner, delete only | base32 secret on the actor |

---

## 9. Export zip (Python, optional HTTP)

Canonical packer: `from app.export import build_zip_bytes`.

```
zip_bytes, result = build_zip_bytes(
    text=document_text,
    spans=spans,
    toggles=user_toggles,
    images=images,
    passphrase=phrase_or_none,
    document_name="payslip",
)
```

Zip layout:

```
privacy-gate-{stem}-{UTC}/
  sanitized.txt
  sanitized.html
  audit.json
  toggles.json
  vault.enc.json          # only if encrypt was used
  HOW_TO_UNLOCK.txt       # only if encrypt was used
  images/...
```

Path names are sanitised. No `../`. HTML escapes field types. If `personal_image` is blacklabel, original photo bytes are omitted.

Suggested endpoint:

`POST /api/export-zip` → `application/zip` (`privacy-gate-payslip.zip`). Body: `{ text, spans, images, toggles, passphrase, document_name }`.

The live browser already downloads HTML/txt/json without this. Add the zip if judges want a folder they can unzip.

---

## 10. Pipeline API FastAPI should expose

Keep [api.md](api.md) for HTTP conventions (JSON, `/api` prefix, error shape `{error, detail}`, 200 fallback on Gemini failure). Change the bodies to match this UI.

| Order | Call | UI trigger | Must |
|---|---|---|---|
| 1 | `GET /api/documents` | S1 sample buttons | Synthetic only. No upload. |
| 2 | `POST /api/detect` | S3 | Local Ollama. 3s timeout. Span contract §6.1. Include `text` + `images`. |
| 3 | (no call) | S4 toggles | State in the browser. |
| 4 | optional `POST /api/export-zip` | S5 download | Python zip. |
| 5 | `POST /api/reason` | S6 send | **Sanitised string only.** |
| 6 | `POST /api/audit` | S8 | Treatments + shared/kept_local + fallback warning. |

Stage gating:

- Detect disabled until a document is chosen.
- Send to Gemini disabled until the user has seen the sanitised preview (`el._result.text`).
- Send disabled if every detected type is blacklabel or encrypt **and** you still want FR-26. The current export panel does **not** block download when everything is hidden. If you enforce FR-26, do it on the Send button, not on Download or Share.

Static serving from FastAPI (update [api.md](api.md) §4):

| Route | File |
|---|---|
| `GET /` | redirect to `/vault/` or a thin shell that links vault + export |
| `GET /vault/` | `app/static/vault/index.html` |
| `GET /privacy-export/` | `app/static/privacy-export/index.html` |
| `GET /theme/` | `app/static/theme/index.html` |
| `GET /static/{path}` | `app/static/{path}` |

CORS is unnecessary if uvicorn serves both. If you split ports, allow the static origin.

---

## 11. Privacy rules the backend must not violate

1. Original document text never appears in `/api/reason`, logs, or QR payloads.
2. Encrypt passphrase never stored, logged, or returned.
3. Creator key never stored inside the `#t=` payload. Only a KDF salt and ciphertext.
4. Share tokens never include the encrypt passphrase.
5. Demo data is invented (A. Okafor, QQ123456C). No real personal data, no PDF upload.
6. Gemma/Ollama may see the original. That is on-device. Gemini may not.

---

## 12. What is already tested

Run:

```
.venv/Scripts/python.exe -m unittest discover -s app -p "test_*.py"
```

Covered today (do not regress):

- Export: overlap, blacklabel isolation, zip path escape, HTML escape, empty passphrase, encrypted zip has no plaintext NI.
- Vault ACL: role ladder, inherit, lock, nested delete, TOTP, share key gate.
- Transfer: round trip, keyed gate, expiry, garbage, tamper, incomplete JSON, URL-safe charset, QR URL length, unicode names.
- QR encoder (needs Node on PATH): SVG for a real `#t=` URL.

Python modules to call instead of reimplementing:

- `app.export.redact.apply_export`
- `app.export.pack.build_zip_bytes`
- `app.export.fields.default_toggles`
- `app.access.Vault`
- `app.access.transfer.pack_file` / `unpack_file`
- `app.access.share.mint_with_key` / `open_token`

---

## 13. Gaps for the backend team (do now vs later)

Do now (needed to connect S3 and S6 to this UI):

1. FastAPI static mount for the three folders in §2.
2. `POST /api/detect` returning §6.4 (nine field types + offsets that match `text`).
3. `POST /api/reason` accepting `PrivacyExport` sanitised text, never originals.
4. UI glue: after detect, `PrivacyExport.mount(slot, result.payslip)`. After Send, render S7 + S8.

Later:

1. Persist vault instead of `localStorage`.
2. `POST /api/export-zip`.
3. Bank statement second document (FR-3). Concatenate sanitised texts with `--- DOCUMENT: NAME ---`.
4. PWA manifest / service worker from [architecture.md](architecture.md). Not required for the vault QR demo.

---

## 14. Mapping from older specs

| Older doc said | Live UI / this spec |
|---|---|
| Streamlit `app.py` ([design.md](design.md)) | Static HTML + JS. ADR-010 still applies. |
| Five field types, income shared by default | Nine identity types, all default blacklabel. Pay stays visible because it is not a type. |
| Consent `shared_types` / `blocked_types` | `toggles`: keep / blacklabel / encrypt |
| Sanitised token `[REDACTED]` | `█` bars or `[BLACKLABELED …]` / `[ENCRYPTED …]` |
| `GET /` → `static/index.html` | `/vault/`, `/privacy-export/`, `/theme/` |
| Share as a signed id in `#s=` | File-in-QR `#t=` gzip payload |
| Detector `detect(text) -> list[Span]` | Same offsets, plus `id`, `kind`, `images` |

[api.md](api.md), [privacy-gate.md](privacy-gate.md), and ADR-011/012/013 were aligned to this file. If a backend change would force the panel to parse a different shape, update this file in the same commit.

---

## Related

- [privacy-gate.md](privacy-gate.md) — functional requirements (S1–S8, Gemini, audit)
- [api.md](api.md) — HTTP conventions (adapt bodies per §10)
- [architecture.md](architecture.md) — FastAPI + PWA process model
- [design.md](design.md) — detector / sanitiser algorithms (still useful). UI layout there is stale.
- Visual screens: `docs/visual/2026-08-22-privacy-gate-screens.html`
- Design canvas: `docs/visual/design-canvas/`
- Python: `app/export/README.md`, `app/access/README.md`
