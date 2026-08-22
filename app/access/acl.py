"""Folder and file access control.

Roles, strongest first: owner, admin, editor, downloader, viewer.
Locked folders hide contents until the lock passphrase is given.
"""

from __future__ import annotations

from dataclasses import dataclass, field

ROLES = ("viewer", "downloader", "editor", "admin", "owner")
RANK = {name: i for i, name in enumerate(ROLES)}

ACTIONS = {
    "view": "viewer",
    "download": "downloader",
    "share": "editor",
    "write": "editor",
    "acl": "admin",
    "lock": "admin",
    "delete": "owner",
}


@dataclass
class Acl:
    owner: str
    members: dict[str, str] = field(default_factory=dict)

    def role_of(self, email: str) -> str | None:
        if email == self.owner:
            return "owner"
        role = self.members.get(email)
        return role if role in RANK else None

    def can(self, email: str, action: str) -> bool:
        need = ACTIONS.get(action)
        if not need:
            return False
        have = self.role_of(email)
        if have is None:
            return False
        return RANK[have] >= RANK[need]

    def grant(self, actor: str, email: str, role: str) -> None:
        if not self.can(actor, "acl"):
            raise PermissionError("only owner or admin can change access")
        if role not in ROLES or role == "owner":
            raise ValueError("role must be viewer, downloader, editor, or admin")
        if email == self.owner:
            raise ValueError("the owner cannot be downgraded")
        self.members[email] = role

    def revoke(self, actor: str, email: str) -> None:
        if not self.can(actor, "acl"):
            raise PermissionError("only owner or admin can change access")
        if email == self.owner:
            raise ValueError("the owner cannot be removed")
        self.members.pop(email, None)

    def to_dict(self) -> dict:
        return {"owner": self.owner, "members": dict(self.members)}

    @classmethod
    def from_dict(cls, raw: dict) -> "Acl":
        return cls(owner=raw["owner"], members=dict(raw.get("members") or {}))


def inherit(parent: Acl, child: Acl) -> Acl:
    """Child wins on the same email. Owner of the child stays the child owner."""
    merged = dict(parent.members)
    merged.update(child.members)
    if parent.owner != child.owner:
        merged.setdefault(parent.owner, "admin")
    return Acl(owner=child.owner, members=merged)
