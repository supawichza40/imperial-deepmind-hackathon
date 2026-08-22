"""Signed share links. The encrypt passphrase is never in the token."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time

KEY_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(text: str) -> bytes:
    pad = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode(text + pad)


def normalize_key(key: str) -> str:
    return "".join(ch for ch in (key or "").upper() if ch.isalnum())


def new_creator_key() -> str:
    raw = "".join(secrets.choice(KEY_ALPHABET) for _ in range(8))
    return f"{raw[:4]}-{raw[4:]}"


def key_mac(secret: bytes, key: str) -> str:
    body = normalize_key(key).encode("ascii")
    return _b64(hmac.new(secret, b"pg-key:" + body, hashlib.sha256).digest()[:16])


def mint(
    secret: bytes,
    *,
    folder_id: str,
    doc_id: str,
    perm: str,
    actor: str,
    ttl_seconds: int = 3600,
    now: float | None = None,
    require_key: bool = False,
) -> str:
    token, _key = mint_with_key(
        secret,
        folder_id=folder_id,
        doc_id=doc_id,
        perm=perm,
        actor=actor,
        ttl_seconds=ttl_seconds,
        now=now,
        require_key=require_key,
    )
    return token


def mint_with_key(
    secret: bytes,
    *,
    folder_id: str,
    doc_id: str,
    perm: str,
    actor: str,
    ttl_seconds: int = 3600,
    now: float | None = None,
    require_key: bool = False,
) -> tuple[str, str | None]:
    if perm not in ("view", "download"):
        raise ValueError("share perm must be view or download")
    clock = time.time() if now is None else now
    creator_key = new_creator_key() if require_key else None
    body = {
        "f": folder_id,
        "d": doc_id,
        "p": perm,
        "by": actor,
        "exp": int(clock) + ttl_seconds,
    }
    if creator_key:
        body["kh"] = key_mac(secret, creator_key)
    payload = _b64(json.dumps(body, separators=(",", ":")).encode("utf-8"))
    sig = _b64(hmac.new(secret, payload.encode("ascii"), hashlib.sha256).digest())
    return f"{payload}.{sig}", creator_key


def open_token(
    secret: bytes,
    token: str,
    now: float | None = None,
    creator_key: str | None = None,
) -> dict:
    try:
        payload, sig = token.split(".", 1)
    except ValueError as e:
        raise ValueError("bad share link") from e
    expect = _b64(hmac.new(secret, payload.encode("ascii"), hashlib.sha256).digest())
    if not hmac.compare_digest(expect, sig):
        raise ValueError("share link was altered")
    try:
        body = json.loads(_unb64(payload))
        folder_id = body["f"]
        doc_id = body["d"]
        perm = body["p"]
        exp = int(body["exp"])
    except (ValueError, TypeError, KeyError, UnicodeDecodeError) as e:
        raise ValueError("bad share link") from e
    clock = time.time() if now is None else now
    if int(exp or 0) < clock:
        raise ValueError("share link expired")
    if perm not in ("view", "download"):
        raise ValueError("share link has no permission")
    needed = body.get("kh")
    if needed:
        if not normalize_key(creator_key or ""):
            raise ValueError("creator key required")
        got = key_mac(secret, creator_key or "")
        if not hmac.compare_digest(got, needed):
            raise ValueError("creator key does not match")
    return {
        "folder_id": folder_id,
        "doc_id": doc_id,
        "perm": perm,
        "actor": body.get("by") or "guest",
        "exp": exp,
        "needs_key": bool(needed),
    }
