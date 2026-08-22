"""Pack a sanitised file into a QR payload another device can open."""

from __future__ import annotations

import gzip
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode

from app.export.crypto import decrypt_bytes, derive_key, encrypt_bytes, new_salt

from .share import normalize_key


def _b64(data: bytes) -> str:
    return urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(text: str) -> bytes:
    pad = "=" * ((4 - len(text) % 4) % 4)
    return urlsafe_b64decode(text + pad)


def pack_file(
    *,
    name: str,
    text: str,
    perm: str = "download",
    ttl_seconds: int = 3600,
    creator_key: str | None = None,
    now: float | None = None,
) -> str:
    if perm not in ("view", "download"):
        raise ValueError("share perm must be view or download")
    clock = int(time.time() if now is None else now)
    exp = clock + ttl_seconds
    if creator_key and normalize_key(creator_key):
        salt = new_salt()
        key = derive_key(normalize_key(creator_key), salt)
        inner = json.dumps({"n": name, "p": perm, "t": text}, separators=(",", ":")).encode("utf-8")
        nonce, ct = encrypt_bytes(key, inner)
        obj = {"v": 1, "x": exp, "k": 1, "s": _b64(salt), "i": _b64(nonce), "c": _b64(ct)}
    else:
        obj = {"v": 1, "n": name, "p": perm, "x": exp, "t": text}
    raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    return _b64(gzip.compress(raw, 9))


def unpack_file(
    payload: str,
    creator_key: str | None = None,
    now: float | None = None,
) -> dict:
    try:
        raw = gzip.decompress(_unb64(payload))
        obj = json.loads(raw)
        exp = int(obj["x"])
    except (KeyError, TypeError, ValueError, OSError) as e:
        raise ValueError("bad transfer payload") from e
    clock = time.time() if now is None else now
    if exp < clock:
        raise ValueError("share link expired")
    if obj.get("k"):
        if not normalize_key(creator_key or ""):
            raise ValueError("creator key required")
        try:
            key = derive_key(normalize_key(creator_key or ""), _unb64(obj["s"]))
            inner = json.loads(decrypt_bytes(key, _unb64(obj["i"]), _unb64(obj["c"])))
        except Exception as e:
            raise ValueError("creator key does not match") from e
        return {
            "name": inner["n"],
            "perm": inner["p"],
            "text": inner["t"],
            "needs_key": True,
        }
    try:
        name = obj["n"]
        perm = obj["p"]
        text = obj["t"]
    except KeyError as e:
        raise ValueError("bad transfer payload") from e
    if perm not in ("view", "download"):
        raise ValueError("share perm must be view or download")
    return {
        "name": name,
        "perm": perm,
        "text": text,
        "needs_key": False,
    }
