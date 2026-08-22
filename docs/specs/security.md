# Privacy Gate — Security Spec

**What this is:** threat model, cryptographic parameters, and security rules for all crypto, vault, QR share, and redaction code in Privacy Gate.
**Covers:** `app/export/crypto.py`, `app/export/redact.py`, `app/export/pack.py`, `app/access/acl.py`, `app/access/store.py`, `app/access/share.py`, `app/access/transfer.py`, `app/access/totp.py`, and the frontend equivalents in `app/static/`.
**Audience:** judges who ask security questions, engineers maintaining the crypto code, anyone reviewing before the demo.

---

## 1. Trust model

```
┌───────────────────────────────────────────────────────────────┐
│ BROWSER (PWA) — trusted with original text                    │
│   Has: full document text, spans, toggles, passphrase         │
│   Does: redaction, encryption, QR packing, vault state        │
└──────────────────────┬────────────────────────────────────────┘
                       │ localhost HTTP (same-origin)
┌──────────────────────▼────────────────────────────────────────┐
│ FASTAPI BACKEND — trusted with original text (for detection)  │
│   Has: full document text (during /api/detect only)           │
│   Does: regex + Gemma detection, Gemini cloud call            │
│   Enforces: only sanitised payload sent to Gemini             │
└──────┬───────────────────────────────┬────────────────────────┘
       │ localhost                      │ HTTPS
┌──────▼──────────┐           ┌────────▼─────────────────────────┐
│ OLLAMA (local)  │           │ GEMINI API (cloud)               │
│ Trusted: yes    │           │ Trusted: NO — sees only sanitised│
│ Sees: full text │           │ text. Never sees originals.      │
└─────────────────┘           └──────────────────────────────────┘
                       │ QR / #t= payload
┌──────────────────────▼────────────────────────────────────────┐
│ GUEST PHONE — untrusted                                       │
│   Has: sanitised text only (or encrypted blob + key needed)   │
│   Cannot: access originals, call Gemini, access vault          │
└───────────────────────────────────────────────────────────────┘
```

### Trust boundaries

| Boundary | What crosses | What must NOT cross |
|---|---|---|
| Browser → FastAPI | full document text (for detection) | nothing restricted (same machine) |
| FastAPI → Ollama | full document text | nothing restricted (local) |
| FastAPI → Gemini | sanitised payload only | original text, spans, API keys |
| Browser → QR | sanitised text (or encrypted blob) | original text, passphrase, creator key (in URL) |
| Guest → Vault | sanitised text (from QR) | originals, vault state, HMAC secret |

**Note on `app/access/store.py:Vault`:** this is a Python class that mirrors the browser vault logic for server-side testing and potential future REST endpoints. In the current demo, the vault runs entirely in the browser (`localStorage["pg-vault-v1"]`). The `Vault` class is not wired to any live endpoint — it exists so that ACL, lock, delete, and share logic can be tested in Python. If FastAPI vault endpoints are built (ui.md §7.4), the `Vault` class would hold the HMAC secret and document text server-side, which would change the trust boundary. Until then, the browser is the sole vault runtime.

### Secrets inventory

| Secret | Who generates | Where stored | Where never stored |
|---|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio | `.env` file (gitignored) | code, logs, commits, QR |
| Export passphrase | user (typed) | browser memory only | zip, HTML, QR, audit, logs |
| Creator key | `new_creator_key()` | shown once in share modal | QR payload, vault, logs |
| Folder lock passphrase | user (typed) | PBKDF2 hash + salt on folder | plaintext, logs |
| TOTP secret | `new_secret()` | actor record, localStorage | QR, share tokens, logs |
| Vault HMAC secret | `os.urandom(32)` | `localStorage["pg-vault-v1"]` | QR, share tokens, network |
| AES-GCM key | `derive_key(passphrase, salt)` | browser memory only | disk, QR, logs |

---

## 2. Cryptographic parameters

### 2.1 Export encryption (AES-GCM)

| Parameter | Value | Source |
|---|---|---|
| Algorithm | AES-256-GCM (authenticated) | `cryptography.hazmat.primitives.ciphers.aead.AESGCM` |
| Key derivation | PBKDF2-HMAC-SHA256 | `PBKDF2HMAC` |
| Iterations | 210,000 | `KDF_ITERS` in `crypto.py` — above OWASP 2023 minimum (600k for SHA256, but 210k is the built value; see §7) |
| Salt length | 16 bytes (random per export) | `SALT_LEN` |
| Nonce length | 12 bytes (random per item) | `NONCE_LEN` — NIST SP 800-38D recommends 96-bit |
| Key length | 32 bytes (256-bit) | `KEY_LEN` |
| AAD | None (associated data not used — see §6 limitation #9) | — |
| Version | 1 | `VERSION` |

**Fresh nonce per item:** each encrypted field gets a new random nonce (`secrets.token_bytes(12)`). Never reused with the same key.

**Passphrase handling:**
- Empty/whitespace-only passphrase is rejected (`ValueError`).
- Passphrase is never written to the zip, HTML, audit JSON, QR, or logs.
- If the user forgets it, the encrypted vault is unrecoverable. This is the design.

### 2.2 Folder lock (PBKDF2 hash)

| Parameter | Value | Source |
|---|---|---|
| Algorithm | PBKDF2-HMAC-SHA256 | `hashlib.pbkdf2_hmac` |
| Iterations | 210,000 | `_hash_lock` in `store.py` |
| Salt length | 16 bytes (random per lock) | `os.urandom(16)` |
| Hash length | 32 bytes | default output |
| Comparison | `hmac.compare_digest` (constant-time) | `store.py:104` |

**Lock enforcement:** locked + not unlocked → docs hidden, download disabled, share disabled. Parent lock blocks child write/list.

### 2.3 QR share — instant transfer (`#t=`)

| Parameter | Value | Source |
|---|---|---|
| Encoding | JSON → gzip (level 9) → urlsafe base64 (no padding) | `transfer.py:pack_file` |
| Unkeyed payload | `{v, n, p, x, t}` — name, perm, expiry, sanitised text | `transfer.py:44` |
| Keyed payload | `{v, x, k, s, i, c}` — expiry, flag, salt, nonce, ciphertext | `transfer.py:42` |
| Keyed encryption | AES-GCM-256, key derived from creator key via PBKDF2 | same params as §2.1 |
| Inner plaintext (keyed) | `{n, p, t}` — name, perm, sanitised text | `transfer.py:40` |
| Max URL length | 2900 bytes UTF-8 (QR version 40, ECC LOW) | `ui.md §5.3` |
| Expiry | unix timestamp, 3600 or 86400 seconds | `transfer.py:36` |

**Creator key:**
- Format: `XXXX-XXXX` (8 chars from 32-char alphabet)
- Alphabet: `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` (no O, I, 0, 1 — avoids ambiguity)
- Normalization: uppercase, alnum only (`normalize_key`)
- Never embedded in the QR payload — only KDF salt + ciphertext travel in the URL
- Keyed packs with the same inputs must not be identical (fresh salt/nonce per pack)

**Unkeyed QR:** the sanitised text is in the URL in plaintext (gzipped but not encrypted). This is acceptable because the text is already sanitised — no originals. The `#t=` fragment is not sent to the server (it's after the hash).

### 2.4 QR share — signed pointer (`#s=`)

| Parameter | Value | Source |
|---|---|---|
| Algorithm | HMAC-SHA256 | `share.py:mint_with_key` |
| Secret | 32-byte random per vault | `store.py:48` |
| Body fields | `f` (folder), `d` (doc), `p` (perm), `by` (actor), `exp`, optional `kh` (key hash) | `share.py:77` |
| Comparison | `hmac.compare_digest` (constant-time) | `share.py:102` |
| Key hash | first 16 bytes of HMAC of `pg-key:` + normalized key | `share.py:34` |

**Scope limitation:** `#s=` tokens are bound to the vault's HMAC secret, which lives in `localStorage`. A second phone does not have this secret. `#s=` is for same-browser testing only. **Do not use `#s=` in the demo QR.**

### 2.5 TOTP (two-step delete)

| Parameter | Value | Source |
|---|---|---|
| Algorithm | HMAC-SHA1, RFC 6238 | `totp.py` |
| Step | 30 seconds | `STEP` |
| Digits | 6 | `DIGITS` |
| Secret | 20 bytes, base32 | `new_secret()` |
| Verification window | ±1 step (previous, current, and next — 90-second total validity) | `verify_totp(window=1)` checks `range(-1, 2)` |
| Comparison | `hmac.compare_digest` (constant-time) | `totp.py:44` |

**Purpose:** TOTP is required only for folder deletion (two-step delete: typed folder name + TOTP code). Not used for login or encryption.

### 2.6 Vault HMAC secret

| Parameter | Value | Source |
|---|---|---|
| Generation | `os.urandom(32)` | `store.py:48` |
| Storage | `localStorage["pg-vault-v1"]` | browser |
| Use | signing `#s=` share tokens | `share.py` |
| Lifetime | per-browser, not persisted server-side | cleared if localStorage cleared |

---

## 3. Redaction security

### 3.1 The privacy boundary

The system enforces one hard rule: **original document text never appears in `/api/reason`, logs, or QR payloads.**

| Path | Sees original? | Sees sanitised? |
|---|---|---|
| Browser | yes | yes |
| FastAPI `/api/detect` | yes (temporarily) | no (returns spans, not redacted text) |
| Ollama (local) | yes | no |
| Gemini (cloud) | **never** | yes (only after consent) |
| QR `#t=` unkeyed | no | yes (gzipped plaintext in URL) |
| QR `#t=` keyed | no | yes (AES-GCM encrypted) |
| Export zip | no | yes (sanitised.txt + HTML) |
| Export zip vault.enc.json | no | encrypted blobs only (passphrase not in zip) |

### 3.2 Redaction tokens

| Treatment | Text replacement | Image handling |
|---|---|---|
| `keep` | unchanged, green highlight in HTML | shown |
| `blacklabel` | `█` bars (same length, max 48) or `[BLACKLABELED TYPE]` | original bytes omitted from zip, placeholder file |
| `encrypt` | `[ENCRYPTED TYPE]` in text, actual value in vault.enc.json | data_url encrypted, plaintext removed |

**Critical:** `█` bars and `[ENCRYPTED ...]` are visually distinct. A user can tell at a glance whether a field is blacklabeled (gone) or encrypted (recoverable with passphrase).

### 3.3 Span overlap handling

`_drop_overlapping` in `redact.py` keeps earlier spans and drops later overlapping ones. This is simpler than the two-pass merge in the design doc — the export code processes spans in `(start, end, id)` order and skips any span that overlaps a previously taken interval. This guarantees non-overlapping replacements, which is sufficient for correctness (reverse-offset replacement works on non-overlapping spans).

### 3.4 Export zip path safety

`_safe_stem` in `pack.py` sanitises the document name: only alnum, `-`, `_`, `.` allowed; everything else becomes `-`. Stripped of leading/trailing `.-`. Truncated to 80 chars. No `../` possible.

HTML in the zip escapes field types and values (`html.escape` with `quote=True`).

---

## 4. Vault access control

### 4.1 Role ladder

`viewer < downloader < editor < admin < owner`

| Action | Minimum role |
|---|---|
| view | viewer |
| download | downloader |
| share | editor |
| write (new folder/doc) | editor |
| acl (grant/revoke) | admin |
| lock | admin |
| delete | owner |

**Owner cannot be granted or removed.** Grant roles are only `viewer`, `downloader`, `editor`, `admin`.

### 4.2 ACL inheritance

Child folders inherit parent members. Child wins on the same email. If parent owner ≠ child owner, parent owner is at least `admin` on the child.

Effective ACL is computed by walking the folder path to root and merging at each level (`_effective` in `store.py`).

### 4.3 Lock enforcement

- Locked + not unlocked → hide docs, disable download and share.
- Parent lock also blocks child write/list (`_need_unlocked` walks parent chain).
- Unlock requires the passphrase, verified via constant-time PBKDF2 hash comparison.
- Empty passphrase is rejected.

### 4.4 Two-step delete

1. Typed folder name must match exactly (after strip).
2. 6-digit TOTP code, verified with ±1 step window.

Deletes the folder and all descendant folders and their docs. This is irreversible.

### 4.5 Share link validation

- `#s=` tokens are HMAC-signed. Tampering is detected via `hmac.compare_digest`.
- Expired tokens are rejected.
- `perm` must be `view` or `download`.
- If `kh` (key hash) is present, creator key is required and verified via constant-time HMAC comparison.

---

## 5. Threats considered

### 5.1 Original text leakage to Gemini

**Threat:** original document text reaches the cloud.
**Mitigation:** `reasoner.py` only accepts a `sanitised_payload: str` parameter. It has no parameter for original text. The API endpoint `/api/reason` only receives `sanitised_payload`. The browser sends only the `PrivacyExport` result text. Defense is in depth: the function signature, the API schema, and the frontend all enforce this.

**Residual risk:** a bug in the frontend that sends `text` instead of `el._result.text`. Mitigated by the API schema (`ReasonRequest` has only `sanitised_payload`).

### 5.2 Passphrase leakage

**Threat:** export passphrase is stored or transmitted.
**Mitigation:** passphrase is used only in-browser to derive an AES-GCM key. It is never sent to the backend, never written to the zip, never included in the audit JSON, never logged. The zip's `vault.enc.json` contains only salt, nonce, and ciphertext.

**Residual risk:** browser memory dump. Accepted — the passphrase is ephemeral.

**Whitespace note:** `derive_key` itself only checks `if not passphrase` (rejects empty string, not whitespace). Whitespace stripping is enforced at the caller level (`store.py` and `redact.py` reject whitespace-only passphrases before calling `derive_key`). This is a defense-in-depth gap — the crypto primitive doesn't validate, the callers do.

### 5.3 Creator key in QR URL

**Threat:** creator key is embedded in the `#t=` URL.
**Mitigation:** the URL contains only KDF salt and AES-GCM ciphertext. The key is derived from the creator key + salt. The creator key itself is shown once to the creator in the share modal and is not in the URL. A guest must type the key to decrypt.

**Residual risk:** the creator key is 8 characters from a 32-char alphabet (~40 bits). Brute force is feasible offline if an attacker has the QR. This is a demo-grade tradeoff — the key is short enough to type on a phone.

### 5.4 QR payload tampering

**Threat:** someone modifies the `#t=` payload in transit.
**Mitigation:** 
- Unkeyed: no integrity protection. The payload is sanitised text — tampering changes what the guest sees but doesn't expose originals.
- Keyed: AES-GCM provides authentication for the inner ciphertext. Tampering with `c` or `i` is detected on decryption (GCM tag verification fails).

**Residual risk (keyed):** the outer envelope fields (`x` expiry, `v` version, `k` flag, `s` salt) are NOT authenticated by AES-GCM — they're in the unencrypted outer JSON. An attacker can modify `x` (extend expiry) without breaking the GCM tag. See §6 limitation #9.

### 5.5 Vault HMAC secret compromise

**Threat:** someone reads `localStorage["pg-vault-v1"]` and forges share tokens.
**Mitigation:** `#s=` tokens are same-browser only. The demo uses `#t=` (instant transfer) which doesn't need the HMAC secret. If localStorage is compromised, the attacker can forge `#s=` tokens but cannot access original document text (it's not in the vault state — only sanitised copies are shared).

### 5.6 Timing attacks on comparisons

**Threat:** attacker measures response time to guess passphrases/TOTP codes.
**Mitigation:** all comparisons use `hmac.compare_digest` (constant-time): folder lock hash, TOTP code, share token signature, creator key hash.

### 5.7 Replay attacks on share tokens

**Threat:** someone reuses an expired share link.
**Mitigation:** tokens carry an `exp` (expiry) timestamp. `open_token` and `unpack_file` both check `exp < now` and raise `ValueError("share link expired")`. However, for keyed `#t=` payloads, the `exp` field is in the unauthenticated outer envelope (see §5.4 residual risk).

### 5.8 Decompression bomb

**Threat:** a crafted `#t=` payload decompresses to a very large buffer, crashing the guest's browser or the Python `unpack_file`.
**Mitigation:** none currently. `gzip.decompress()` and `json.loads()` have no output-size cap. See §6 limitation #10.

### 5.9 TOTP brute force

**Threat:** attacker repeatedly guesses 6-digit TOTP codes to trigger folder deletion.
**Mitigation:** none currently — no rate limiting or lockout. The 3-step window (±1) means 3 valid codes at any time, giving a 3/1,000,000 chance per guess. See §6 limitation #4.

### 5.10 Silent downgrade to unkeyed transfer

**Threat:** `pack_file` is called with a `creator_key` that normalizes to empty (e.g. all symbols), silently producing an unkeyed (plaintext) pack instead of raising.
**Mitigation:** callers should validate the key before calling `pack_file`. The function's `if creator_key and normalize_key(creator_key):` check is a fail-open path. Impact is limited — only sanitised text is in the payload — but the caller may not know the pack is unencrypted.

### 5.11 Vault item ciphertext swapping

**Threat:** someone with write access to `vault.enc.json` reorders or swaps same-length ciphertext blobs between items, causing a decrypted value to be attributed to the wrong field.
**Mitigation:** none currently. AES-GCM authenticates each ciphertext independently but nothing binds a ciphertext to its `id`/`type`/position. Binding `id` and `type` as AAD would fix this. See §6 limitation #9.

### 5.12 Global unlock state

**Threat:** in the Python `Vault` class, `folder.unlocked = True` is a global flag. Once one actor unlocks a folder, all actors bypass lock checks until re-lock.
**Mitigation:** in the browser demo, only one actor exists (`you@local`), so this is not exploitable. If the `Vault` class is wired to multi-user REST endpoints, unlock must be session-scoped. See §6 limitation #11.

---

## 6. What is NOT security-hardened (honest limitations)

This is a hackathon project. The following are NOT production-grade:

1. **Vault state is in `localStorage`** — not encrypted at rest in the browser. Anyone with access to the browser's dev tools can read it. A production version would use IndexedDB with encryption or server-side storage.
2. **Creator key is 40 bits** — brute-forceable offline with the QR payload. Acceptable for a demo; not for production.
3. **TOTP secret is in `localStorage`** — visible in dev tools. A production version would store it server-side or in a secure enclave.
4. **No rate limiting on passphrase attempts** — folder lock and export passphrase can be brute-forced without throttling. The 210,000-iteration PBKDF2 slows this but doesn't prevent it.
5. **`#t=` unkeyed QR has no integrity protection** — the sanitised text in the URL can be modified by anyone who has the QR. The text is already sanitised so no originals leak, but the guest might see altered content.
6. **No CSRF protection on FastAPI endpoints** — the API is localhost-only and same-origin, so CSRF is not exploitable in the demo configuration. A deployed version would need CSRF tokens.
7. **PWA service worker caches static shell** — if the app is updated, the old cached version may be served. Cache-busting query params or versioned filenames would be needed in production.
8. **PBKDF2 iterations (210,000) are below OWASP 2023 recommendation (600,000 for SHA-256).** The built value works but should be raised for production.
9. **No AAD binding on AES-GCM ciphertexts.** In the export vault (`vault.enc.json`) and keyed QR transfers (`#t=`), the outer metadata (expiry, version, field id/type) is not bound to the ciphertext as Associated Authenticated Data. This means: (a) expiry in keyed QR can be tampered without breaking GCM authentication, (b) vault item ciphertexts can be reordered/swapped between fields. Binding `id`/`type`/`exp` as AAD would fix both. Accepted for demo — the impact is on sanitised data, not originals.
10. **No decompression size limit on `unpack_file`.** `gzip.decompress()` has no output cap. A crafted QR payload could decompress to a very large buffer. A production version would cap decompressed size (e.g. 1 MB).
11. **Global unlock state in Python `Vault` class.** `folder.unlocked = True` is instance-wide, not session-scoped. In the browser demo (single actor), this is not exploitable. If wired to multi-user REST endpoints, unlock must be per-session.
12. **TOTP brute force has no throttling.** The 6-digit code with a 3-step window and no lockout is guessable with enough attempts. A production version would rate-limit TOTP verification.
13. **Silent fail-open on empty creator key.** `pack_file` with a `creator_key` that normalizes to empty silently produces an unkeyed (plaintext) pack instead of raising. Callers must validate the key before calling.

**Framing for judges:** "This is assisted redaction with human approval, not guaranteed anonymisation. The crypto is real AES-GCM-256 with PBKDF2 key derivation, but the key management is demo-grade. A production version would use a hardware-backed key store, server-side rate limiting, AAD-bound ciphertexts, and encrypted-at-rest vault storage."

---

## 7. Cryptographic parameter review

| Parameter | Built value | OWASP/NIST recommendation | Status |
|---|---|---|---|
| PBKDF2 iterations | 210,000 | OWASP 2023: 600,000 for SHA-256 | below recommendation — acceptable for demo, raise for production |
| PBKDF2 salt | 16 bytes random | NIST: ≥ 16 bytes | ✅ meets minimum |
| AES-GCM nonce | 12 bytes random | NIST SP 800-38D: 96-bit | ✅ correct |
| AES-GCM key | 32 bytes (256-bit) | NIST: 128, 192, or 256 | ✅ 256-bit |
| TOTP | SHA-1, 30s, 6 digits, ±1 window | RFC 6238 | ✅ standard |
| HMAC | SHA-256 | NIST: SHA-256 acceptable | ✅ correct |
| Creator key entropy | ~40 bits (8 × 5 bits) | NIST SP 800-63: ≥ 112 bits for shared secrets | below — demo tradeoff |
| Constant-time comparison | `hmac.compare_digest` | required for all security comparisons | ✅ used everywhere |

---

## 8. Test coverage for security properties

Already tested (do not regress — see `app/access/test_*.py`, `app/export/test_export.py`):

| Test | What it verifies |
|---|---|
| Export overlap | overlapping spans don't corrupt output |
| Blacklabel isolation | blacklabeled text is replaced, not leaked |
| Zip path escape | `../` in document name is sanitised |
| HTML escape | field types and values are escaped in HTML output |
| Empty passphrase | encrypt without passphrase → `ValueError` |
| Encrypted zip has no plaintext NI | vault.enc.json does not contain plaintext sensitive values |
| Vault ACL role ladder | each role can/cannot do the expected actions |
| Vault ACL inheritance | child inherits parent members, child wins |
| Vault lock | locked folder hides docs, unlock needs passphrase |
| Vault nested delete | delete removes descendants |
| Vault TOTP | correct code passes, wrong code fails, expired code fails |
| Vault share key gate | keyed token without key → rejected |
| Transfer round trip | pack → unpack produces same text |
| Transfer keyed gate | keyed pack without key → `ValueError` |
| Transfer expiry | expired pack → `ValueError` |
| Transfer garbage | invalid base64/gzip/JSON → `ValueError("bad transfer payload")` |
| Transfer tamper | modified payload → `ValueError` |
| Transfer incomplete JSON | missing `n`/`p`/`t` → `ValueError("bad transfer payload")` |
| Transfer URL-safe charset | payload only contains URL-safe characters |
| Transfer QR URL length | packed URL ≤ 2900 bytes for a blacklabeled sample |
| Transfer unicode names | non-ASCII names survive round trip |

---

## 9. Security checklist for the demo

Before the demo:
- [ ] `.env` is in `.gitignore` (no API key in the repo)
- [ ] No real personal data in any fixture
- [ ] Ollama is running locally (detection works with wifi off)
- [ ] Export passphrase is typed live (not pre-filled)
- [ ] QR demo uses `#t=` (not `#s=`)
- [ ] If showing encryption: passphrase is not shown on screen after typing

During the demo:
- [ ] Say "assisted redaction with human approval" — never "anonymisation"
- [ ] Show the sanitised payload before sending to Gemini (the pitch moment)
- [ ] Show the audit log at the end
- [ ] If asked about limitations: be honest about localStorage, creator key entropy, and PBKDF2 iterations

---

## Related

- [Requirements spec](privacy-gate.md) — functional requirements, privacy rules
- [UI spec](ui.md) — frontend modules, data contracts, vault/ACL/QR documentation
- [Architecture spec](architecture.md) — system architecture, trust boundaries
- [API spec](api.md) — endpoint definitions
- [Decisions index](../decisions/index.md) — ADRs including ADR-012 (3-state consent with encryption)