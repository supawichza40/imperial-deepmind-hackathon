"""Field types the export toggles understand.

The detector (other teammates) should emit spans with these `type` values.
Unknown types still work: they show up as extra toggles.
"""

from __future__ import annotations

KEEP = "keep"
BLACKLABEL = "blacklabel"
ENCRYPT = "encrypt"
ACTIONS = (KEEP, BLACKLABEL, ENCRYPT)

# Shown in the panel even when a document has none, so the UI is stable.
FIELD_TYPES = (
    "name",
    "address",
    "ni_number",
    "account_number",
    "email",
    "phone",
    "date_of_birth",
    "signature",
    "personal_image",
)

LABELS = {
    "name": "Name",
    "address": "Address",
    "ni_number": "NI number",
    "account_number": "Account number",
    "email": "Email",
    "phone": "Phone",
    "date_of_birth": "Date of birth",
    "signature": "Signature",
    "personal_image": "Personal photo",
}

# Identity-shaped types start ON as blacklabel. Money and dates stay visible
# unless the user flips them.
DEFAULT_ON = frozenset({
    "name",
    "address",
    "ni_number",
    "account_number",
    "email",
    "phone",
    "date_of_birth",
    "signature",
    "personal_image",
})


def default_toggles(present_types: list[str] | None = None) -> dict[str, str]:
    types = list(FIELD_TYPES)
    if present_types:
        for t in present_types:
            if t not in types:
                types.append(t)
    return {
        t: (BLACKLABEL if t in DEFAULT_ON else KEEP)
        for t in types
    }


def label_for(field_type: str) -> str:
    return LABELS.get(field_type, field_type.replace("_", " ").title())
