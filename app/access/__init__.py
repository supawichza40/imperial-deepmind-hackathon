"""Folders, share links, and two-step delete for Privacy Gate.

    from app.access import Vault

    vault = Vault()
    you = vault.register("you@local")
    inbox = vault.add_folder("you@local", "Inbox")
    doc = vault.add_doc("you@local", inbox.id, "payslip.txt", text="...")
    link = vault.share_link("you@local", doc.id, perm="download")
    vault.delete_folder("you@local", inbox.id, typed_name="Inbox", totp_code="123456")
"""

from .acl import Acl, ROLES, inherit
from .share import mint, open_token
from .store import Vault
from .totp import new_secret, totp, verify_totp

__all__ = [
    "Acl",
    "ROLES",
    "Vault",
    "inherit",
    "mint",
    "new_secret",
    "open_token",
    "totp",
    "verify_totp",
]
