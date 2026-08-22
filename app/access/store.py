"""In-memory vault of folders and documents with locks and ACLs."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass, field

from .acl import Acl
from .share import mint, open_token
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
    ) -> str:
        doc = self._doc(doc_id)
        folder = self._folder(doc.folder_id)
        self._need(folder, actor, "share")
        self._need_unlocked(folder)
        return mint(
            self.hmac_secret,
            folder_id=folder.id,
            doc_id=doc.id,
            perm=perm,
            actor=actor,
            ttl_seconds=ttl_seconds,
        )

    def open_share(self, token: str) -> tuple[str, Document]:
        claim = open_token(self.hmac_secret, token)
        doc = self._doc(claim["doc_id"])
        if doc.folder_id != claim["folder_id"]:
            raise PermissionError("share link does not match this file")
        folder = self._folder(doc.folder_id)
        if folder.locked and not folder.unlocked:
            raise PermissionError("folder is locked")
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
        gone = [folder_id] + [f.id for f in self.folders.values() if f.parent_id == folder_id]
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

    def _need(self, folder: Folder, actor: str, action: str) -> None:
        if not folder.acl.can(actor, action):
            raise PermissionError(f"{action} is not allowed")

    def _need_unlocked(self, folder: Folder) -> None:
        if folder.locked and not folder.unlocked:
            raise PermissionError("folder is locked")
