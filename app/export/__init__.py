"""Privacy Gate download feature.

Other teammates own the main app. Plug this in as:

    from app.export import build_zip_bytes, apply_export, default_toggles, FIELD_TYPES

    zip_bytes, result = build_zip_bytes(
        text=document_text,
        spans=span_list,          # [{type, start, end, id?, kind?, image_id?, bbox?}]
        toggles=user_toggles,     # {field_type: "keep"|"blacklabel"|"encrypt"}
        images=image_list,        # [{id, data_url, alt?}]
        passphrase=optional_phrase,
        document_name="payslip",
    )

Drop-in UI: open app/static/privacy-export/index.html
or mount the panel with PrivacyExport.mount(element, payload).
"""

from .crypto import decrypt_text, derive_key
from .fields import ACTIONS, FIELD_TYPES, default_toggles, label_for
from .pack import build_zip_bytes
from .redact import apply_export

__all__ = [
    "ACTIONS",
    "FIELD_TYPES",
    "apply_export",
    "build_zip_bytes",
    "default_toggles",
    "label_for",
    "unlock_vault",
]


def unlock_vault(vault: dict, passphrase: str) -> list[dict]:
    """Return plaintext private values from a downloaded vault.enc.json."""
    from base64 import b64decode

    salt = b64decode(vault["salt_b64"])
    key = derive_key(passphrase, salt)
    opened = []
    for item in vault.get("items") or []:
        opened.append({
            "id": item.get("id"),
            "type": item.get("type"),
            "kind": item.get("kind"),
            "value": decrypt_text(key, item),
        })
    return opened
