"""In-memory vault of folders and documents with locks and ACLs."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass

from .acl import Acl, inherit
from .share import mint_with_key, open_token
from .totp import new_secret, verify_totp


def _hash_lock(passphrase: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, 210_000)


@dataclass
class Folder:
    id: str
    name: str
    parent_id: str | None
    acl: Acl
    locked: bool = False
    lock_salt: bytes | None = None
    lock_hash: bytes | None = None
    unlocked: bool = True


@dataclass
class Document:
    id: str
    folder_id: str
    name: str
    text: str = ""


@dataclass
class Actor:
    email: str
    totp_secret: str


class Vault:
    def __init__(self, hmac_secret: bytes | None = None) -> None:
        self.hmac_secret = hmac_secret or os.urandom(32)
        self.actors: dict[str, Actor] = {}
        self.folders: dict[str, Folder] = {}
        self.docs: dict[str, Document] = {}

    def register(self, email: str) -> Actor:
        if email not in self.actors:
            self.actors[email] = Actor(email=email, totp_secret=new_secret())
        return self.actors[email]

    def add_folder(self, actor: str, name: str, parent_id: str | None = None) -> Folder:
        name = (name or "").strip()
        if not name:
            raise ValueError("folder name is required")
        if parent_id:
            parent = self._folder(parent_id)
            self._need(parent, actor, "write")
            self._need_unlocked(parent)
            acl = Acl(owner=parent.acl.owner, members=dict(parent.acl.members))
        else:
            acl = Acl(owner=actor)
        folder = Folder(
            id=secrets.token_hex(8),
            name=name,
            parent_id=parent_id,
            acl=acl,
        )
        self.folders[folder.id] = folder
        return folder

    def add_doc(self, actor: str, folder_id: str, name: str, text: str = "") -> Document:
        folder = self._folder(folder_id)
        self._need(folder, actor, "write")
        self._need_unlocked(folder)
        doc = Document(id=secrets.token_hex(8), folder_id=folder_id, name=name, text=text)
        self.docs[doc.id] = doc
        return doc

    def lock_folder(self, actor: str, folder_id: str, passphrase: str) -> None:
        folder = self._folder(folder_id)
        self._need(folder, actor, "lock")
        if not (passphrase or "").strip():
            raise ValueError("lock passphrase is required")
        salt = os.urandom(16)
        folder.lock_salt = salt
        folder.lock_hash = _hash_lock(passphrase, salt)
        folder.locked = True
        folder.unlocked = False

    def unlock_folder(self, actor: str, folder_id: str, passphrase: str) -> None:
        folder = self._folder(folder_id)
        self._need(folder, actor, "view")
        if not folder.locked or folder.lock_salt is None or folder.lock_hash is None:
            folder.unlocked = True
            return
        got = _hash_lock(passphrase, folder.lock_salt)
        if not hmac.compare_digest(got, folder.lock_hash):
            raise PermissionError("folder lock passphrase does not match")
        folder.unlocked = True

    def list_docs(self, actor: str, folder_id: str) -> list[Document]:
        folder = self._folder(folder_id)
        self._need(folder, actor, "view")
        self._need_unlocked(folder)
        return [d for d in self.docs.values() if d.folder_id == folder_id]

    def download(self, actor: str, doc_id: str) -> Document:
        doc = self._doc(doc_id)
        folder = self._folder(doc.folder_id)
        self._need(folder, actor, "download")
        self._need_unlocked(folder)
        return doc

    def share_link(
        self,
        actor: str,
        doc_id: str,
        perm: str = "download",
        ttl_seconds: int = 3600,
        require_key: bool = False,
    ) -> str:
        token, _key = self.share_with_key(
            actor, doc_id, perm=perm, ttl_seconds=ttl_seconds, require_key=require_key,
        )
        return token

    def share_with_key(
        self,
        actor: str,
        doc_id: str,
        perm: str = "download",
        ttl_seconds: int = 3600,
        require_key: bool = False,
    ) -> tuple[str, str | None]:
        doc = self._doc(doc_id)
        folder = self._folder(doc.folder_id)
        self._need(folder, actor, "share")
        self._need_unlocked(folder)
        return mint_with_key(
            self.hmac_secret,
            folder_id=folder.id,
            doc_id=doc.id,
            perm=perm,
            actor=actor,
            ttl_seconds=ttl_seconds,
            require_key=require_key,
        )

    def open_share(self, token: str, creator_key: str | None = None) -> tuple[str, Document]:
        claim = open_token(self.hmac_secret, token, creator_key=creator_key)
        doc = self._doc(claim["doc_id"])
        if doc.folder_id != claim["folder_id"]:
            raise PermissionError("share link does not match this file")
        folder = self._folder(doc.folder_id)
        self._need_unlocked(folder)
        if claim["perm"] == "view":
            return "view", doc
        return "download", doc

    def delete_folder(
        self,
        actor: str,
        folder_id: str,
        typed_name: str,
        totp_code: str,
    ) -> None:
        folder = self._folder(folder_id)
        self._need(folder, actor, "delete")
        if typed_name.strip() != folder.name:
            raise PermissionError("type the folder name exactly, like GitHub")
        person = self.actors.get(actor)
        if person is None or not verify_totp(person.totp_secret, totp_code):
            raise PermissionError("authenticator code is wrong or expired")
        gone = self._descendants(folder_id)
        for fid in gone:
            self.folders.pop(fid, None)
        self.docs = {i: d for i, d in self.docs.items() if d.folder_id not in gone}

    def _folder(self, folder_id: str) -> Folder:
        folder = self.folders.get(folder_id)
        if not folder:
            raise KeyError("folder not found")
        return folder

    def _doc(self, doc_id: str) -> Document:
        doc = self.docs.get(doc_id)
        if not doc:
            raise KeyError("file not found")
        return doc

    def _effective(self, folder: Folder) -> Acl:
        path: list[Folder] = []
        cur: Folder | None = folder
        seen: set[str] = set()
        while cur is not None and cur.id not in seen:
            seen.add(cur.id)
            path.append(cur)
            cur = self.folders.get(cur.parent_id) if cur.parent_id else None
        path.reverse()
        acc = path[0].acl
        for node in path[1:]:
            acc = inherit(acc, node.acl)
        return acc

    def _descendants(self, folder_id: str) -> set[str]:
        found = {folder_id}
        changed = True
        while changed:
            changed = False
            for folder in self.folders.values():
                if folder.parent_id in found and folder.id not in found:
                    found.add(folder.id)
                    changed = True
        return found

    def _need(self, folder: Folder, actor: str, action: str) -> None:
        if not self._effective(folder).can(actor, action):
            raise PermissionError(f"{action} is not allowed")

    def _need_unlocked(self, folder: Folder) -> None:
        cur: Folder | None = folder
        seen: set[str] = set()
        while cur is not None and cur.id not in seen:
            seen.add(cur.id)
            if cur.locked and not cur.unlocked:
                raise PermissionError("folder is locked")
            cur = self.folders.get(cur.parent_id) if cur.parent_id else None
