# Folders, share links, and two-step delete

Open `app/static/vault/index.html` (serve the `app/static` folder over http so share links copy cleanly).

What you get
- Download and Share file buttons
- A share QR, plus an optional creator key that is not in the QR
- Folders with inherited access
- Folder lock with a passphrase
- Roles. owner, admin, editor, downloader, viewer
- Delete needs the folder name typed exactly, plus a 6 digit authenticator code

Turn on Ask for my key when you share. You see a one time key. The QR holds the sanitised file, not a pointer into this laptop. A phone on the same WiFi can scan and open it. The encrypt passphrase is never in the QR.

This is assisted access control for the demo. It is not a production identity provider. Share links never include the encrypt passphrase.

Python

```
from app.access import Vault
vault = Vault()
vault.register("you@local")
```

Run tests with `.venv/Scripts/python.exe app/access/test_access.py`.
