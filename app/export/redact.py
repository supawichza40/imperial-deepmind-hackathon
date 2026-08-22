"""Turn a document + span list + per-type toggles into a downloadable copy.

Spans use the team contract from the visual explainer:
  {id?, type, start, end, kind?}
  kind is "text" (default), "signature", or "personal_image".

Image spans add:
  image_id, bbox  [x, y, w, h] as fractions of the image (0 to 1).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .crypto import (
    VERSION,
    derive_key,
    encrypt_blob,
    encrypt_text,
    new_salt,
)
from .fields import BLACKLABEL, ENCRYPT, KEEP, default_toggles, label_for

BLACK_CHAR = "█"


@dataclass
class Span:
    type: str
    start: int
    end: int
    id: str = ""
    kind: str = "text"
    image_id: str = ""
    bbox: list[float] | None = None
    value: str = ""

    @classmethod
    def from_dict(cls, raw: dict, index: int) -> "Span":
        start = int(raw["start"])
        end = int(raw["end"])
        if end < start:
            raise ValueError("span end must be at or after start")
        return cls(
            type=str(raw.get("type") or "unknown"),
            start=start,
            end=end,
            id=str(raw.get("id") or f"s{index}"),
            kind=str(raw.get("kind") or "text"),
            image_id=str(raw.get("image_id") or ""),
            bbox=list(raw["bbox"]) if raw.get("bbox") else None,
            value=str(raw.get("value") or ""),
        )


@dataclass
class ImageAsset:
    id: str
    data_url: str = ""
    mime: str = "image/png"
    alt: str = "attached image"

    @classmethod
    def from_dict(cls, raw: dict, index: int) -> "ImageAsset":
        return cls(
            id=str(raw.get("id") or f"img{index}"),
            data_url=str(raw.get("data_url") or ""),
            mime=str(raw.get("mime") or "image/png"),
            alt=str(raw.get("alt") or "attached image"),
        )


@dataclass
class ExportResult:
    text: str
    html: str
    audit: list[dict]
    vault: dict | None
    salt_b64: str | None
    images: list[dict] = field(default_factory=list)
    toggles: dict[str, str] = field(default_factory=dict)


def _black_bar(length: int) -> str:
    n = max(length, 1)
    return BLACK_CHAR * min(n, 48)


def _placeholder(action: str, field_type: str) -> str:
    name = label_for(field_type).upper()
    if action == ENCRYPT:
        return f"[ENCRYPTED {name}]"
    return f"[BLACKLABELED {name}]"


def apply_export(
    text: str,
    spans: list[dict],
    toggles: dict[str, str] | None = None,
    images: list[dict] | None = None,
    passphrase: str | None = None,
) -> ExportResult:
    parsed = _drop_overlapping(
        [Span.from_dict(s, i) for i, s in enumerate(spans)],
        len(text),
    )
    assets = [ImageAsset.from_dict(im, i) for i, im in enumerate(images or [])]
    present = sorted({s.type for s in parsed})
    actions = default_toggles(present)
    if toggles:
        actions.update({k: v for k, v in toggles.items() if v in (KEEP, BLACKLABEL, ENCRYPT)})

    needs_encrypt = any(actions.get(s.type) == ENCRYPT for s in parsed)
    key = salt = None
    vault_items: list[dict] = []
    if needs_encrypt:
        if not (passphrase or "").strip():
            raise ValueError("a passphrase is required when any toggle is set to encrypt")
        salt = new_salt()
        key = derive_key(passphrase, salt)

    # Apply from the end so earlier offsets stay valid.
    ordered = sorted(parsed, key=lambda s: (s.start, s.end), reverse=True)
    out = text
    audit: list[dict] = []
    for span in ordered:
        action = actions.get(span.type, KEEP)
        is_text = 0 <= span.start < span.end <= len(text)
        original = span.value or (text[span.start:span.end] if is_text else "")
        entry = {
            "id": span.id,
            "type": span.type,
            "kind": span.kind,
            "action": action,
            "start": span.start,
            "end": span.end,
        }
        if action == KEEP:
            entry["left_visible"] = True
            audit.append(entry)
            continue

        if action == ENCRYPT and key is not None:
            secret = original or (span.kind + ":" + span.image_id)
            item: dict[str, Any] = {
                "id": span.id,
                "type": span.type,
                "kind": span.kind,
                **encrypt_text(key, secret),
            }
            if span.kind in ("signature", "personal_image") and span.image_id:
                asset = next((a for a in assets if a.id == span.image_id), None)
                if asset and asset.data_url:
                    item["image"] = {
                        "id": asset.id,
                        **encrypt_text(key, asset.data_url),
                    }
            vault_items.append(item)

        if not is_text:
            entry["image_id"] = span.image_id
            audit.append(entry)
            continue

        replacement = _placeholder(action, span.type)
        if action == BLACKLABEL:
            replacement = _black_bar(len(original))
        out = out[:span.start] + replacement + out[span.end:]
        entry["replacement"] = replacement
        audit.append(entry)

    audit.sort(key=lambda e: e.get("start", 0))
    html = _to_html(text, parsed, actions)
    image_export = _export_images(assets, parsed, actions, key)

    vault = None
    salt_b64 = None
    if vault_items and salt is not None:
        from base64 import b64encode
        salt_b64 = b64encode(salt).decode("ascii")
        vault = {
            "v": VERSION,
            "kdf": "pbkdf2-sha256",
            "iterations": 210000,
            "salt_b64": salt_b64,
            "items": list(reversed(vault_items)),
        }

    return ExportResult(
        text=out,
        html=html,
        audit=audit,
        vault=vault,
        salt_b64=salt_b64,
        images=image_export,
        toggles=actions,
    )


def _to_html(text: str, spans: list[Span], actions: dict[str, str]) -> str:
    """Highlighted HTML of the original, with chosen treatment per span."""
    parts: list[str] = []
    last = 0
    for span in sorted(spans, key=lambda s: s.start):
        if span.kind not in ("text",) and span.start == span.end:
            continue
        if span.start < last or span.end > len(text):
            continue
        parts.append(_esc(text[last:span.start]))
        chunk = _esc(text[span.start:span.end])
        action = actions.get(span.type, KEEP)
        label = label_for(span.type)
        if action == KEEP:
            parts.append(
                f'<mark class="keep" data-type="{_esc(span.type)}">{chunk}</mark>'
            )
        elif action == BLACKLABEL:
            bar = _esc(_black_bar(span.end - span.start))
            parts.append(
                f'<mark class="blacklabel" title="{_esc(label)} blacklabeled">{bar}</mark>'
            )
        else:
            parts.append(
                f'<mark class="encrypt" title="{_esc(label)} encrypted">'
                f"{_esc(_placeholder(ENCRYPT, span.type))}</mark>"
            )
        last = span.end
    parts.append(_esc(text[last:]))
    return '<pre class="doc">' + "".join(parts) + "</pre>"


def _export_images(
    assets: list[ImageAsset],
    spans: list[Span],
    actions: dict[str, str],
    key: bytes | None,
) -> list[dict]:
    out = []
    for asset in assets:
        related = [s for s in spans if s.image_id == asset.id]
        boxes = []
        for span in related:
            action = actions.get(span.type, KEEP)
            if action == KEEP:
                continue
            box = {
                "id": span.id,
                "type": span.type,
                "action": action,
                "bbox": span.bbox or [0.05, 0.75, 0.4, 0.18],
            }
            boxes.append(box)
        item = {
            "id": asset.id,
            "alt": asset.alt,
            "mime": asset.mime,
            "data_url": asset.data_url,
            "boxes": boxes,
        }
        hide_whole = any(
            actions.get(s.type) in (BLACKLABEL, ENCRYPT)
            for s in related
        )
        if hide_whole:
            encrypted_wanted = any(
                actions.get(s.type) == ENCRYPT
                for s in related
            )
            whole_action = ENCRYPT if encrypted_wanted else BLACKLABEL
            item["whole"] = whole_action
            if whole_action == ENCRYPT and key is not None:
                item["encrypted"] = encrypt_blob(key, asset.data_url.encode("utf-8"))
                item["data_url"] = ""
            elif whole_action == BLACKLABEL:
                item["data_url"] = ""
                item["blacklabeled"] = True
        out.append(item)
    return out


def _drop_overlapping(spans: list[Span], text_len: int) -> list[Span]:
    """Keep earlier text spans. Skip later ones that overlap so offsets stay valid."""
    kept: list[Span] = []
    taken: list[tuple[int, int]] = []
    for span in sorted(spans, key=lambda s: (s.start, s.end, s.id)):
        is_text = 0 <= span.start < span.end <= text_len
        if not is_text:
            kept.append(span)
            continue
        if any(not (span.end <= a or span.start >= b) for a, b in taken):
            continue
        taken.append((span.start, span.end))
        kept.append(span)
    return kept


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
