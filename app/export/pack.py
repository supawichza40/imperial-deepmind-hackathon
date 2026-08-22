"""Pack a Privacy Gate export into a zip the browser can download."""

from __future__ import annotations

import html
import io
import json
import zipfile
from datetime import datetime, timezone

from .redact import ExportResult, apply_export


def _safe_stem(name: str) -> str:
    cleaned = "".join(
        ch if ch.isalnum() or ch in "-_." else "-"
        for ch in (name or "document")
    )
    cleaned = cleaned.strip(".-") or "document"
    return cleaned[:80]


def build_zip_bytes(
    text: str,
    spans: list[dict],
    toggles: dict[str, str] | None = None,
    images: list[dict] | None = None,
    passphrase: str | None = None,
    document_name: str = "document",
) -> tuple[bytes, ExportResult]:
    result = apply_export(
        text=text,
        spans=spans,
        toggles=toggles,
        images=images,
        passphrase=passphrase,
    )
    buf = io.BytesIO()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    root = f"privacy-gate-{_safe_stem(document_name)}-{stamp}"
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{root}/sanitized.txt", result.text)
        zf.writestr(
            f"{root}/sanitized.html",
            _html_page(result.html, result.images, result.toggles),
        )
        zf.writestr(
            f"{root}/audit.json",
            json.dumps(result.audit, indent=2),
        )
        zf.writestr(
            f"{root}/toggles.json",
            json.dumps(result.toggles, indent=2),
        )
        if result.vault:
            zf.writestr(
                f"{root}/vault.enc.json",
                json.dumps(result.vault, indent=2),
            )
            zf.writestr(
                f"{root}/HOW_TO_UNLOCK.txt",
                "This zip has an encrypted vault.\n"
                "The passphrase is NOT in this file on purpose.\n"
                "Unlock with the same phrase you typed at download.\n"
                "Python: from app.export import unlock_vault\n",
            )
        for img in result.images:
            name = img.get("id") or "image"
            if img.get("blacklabeled") or img.get("whole") == "blacklabel":
                zf.writestr(
                    f"{root}/images/{name}.BLACKLABELED.txt",
                    "Personal image removed. A black label replaced it.\n",
                )
            elif img.get("encrypted") or img.get("whole") == "encrypt":
                zf.writestr(
                    f"{root}/images/{name}.ENCRYPTED.json",
                    json.dumps(img.get("encrypted") or {}, indent=2),
                )
            elif img.get("data_url"):
                zf.writestr(
                    f"{root}/images/{name}.url.txt",
                    img["data_url"],
                )
            if img.get("boxes"):
                zf.writestr(
                    f"{root}/images/{name}.boxes.json",
                    json.dumps(img["boxes"], indent=2),
                )
    return buf.getvalue(), result


def _attr(value: object) -> str:
    return html.escape(str(value), quote=True)


def _html_page(body: str, images: list[dict], toggles: dict[str, str]) -> str:
    cards = []
    for img in images:
        box_bits = []
        for b in img.get("boxes") or []:
            bbox = b.get("bbox") or []
            if len(bbox) < 4:
                continue
            action = _attr(b.get("action") or "")
            box_bits.append(
                f'<i class="{action}" style="'
                f"left:{float(bbox[0])*100}%;top:{float(bbox[1])*100}%;"
                f"width:{float(bbox[2])*100}%;height:{float(bbox[3])*100}%"
                f'" title="{_attr(b.get("type"))} {action}"></i>'
            )
        boxes = "".join(box_bits)
        if img.get("blacklabeled") or img.get("whole") == "blacklabel":
            frame = '<div class="photo black">photo blacklabeled</div>'
        elif img.get("whole") == "encrypt" or img.get("encrypted"):
            frame = '<div class="photo enc">photo encrypted</div>'
        elif img.get("data_url"):
            frame = (
                f'<div class="photo"><img src="{_attr(img["data_url"])}" alt="">'
                f"{boxes}</div>"
            )
        else:
            frame = ""
        if frame:
            cards.append(frame)
    gallery = "\n".join(cards)
    toggle_rows = "".join(
        f"<li><code>{_attr(k)}</code> {_attr(v)}</li>" for k, v in toggles.items()
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8">
<title>Privacy Gate export</title>
<style>
body{{font:15px/1.5 -apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#f7f7f5;color:#16171a;margin:24px}}
.doc{{background:#fff;border:1px solid #e3e3df;padding:16px;border-radius:8px;white-space:pre-wrap}}
mark.blacklabel{{background:#111;color:#111;border-radius:2px}}
mark.encrypt{{background:#111f33;color:#7db1f5}}
mark.keep{{background:#e8f6ee;color:#1a7f4b}}
.photo{{position:relative;display:inline-block;max-width:280px;margin:12px 12px 0 0;border:1px solid #e3e3df}}
.photo img{{display:block;width:280px;height:auto}}
.photo i{{position:absolute;background:#111}}
.photo i.encrypt{{background:#1e3a5f}}
.photo.black,.photo.enc{{width:280px;height:160px;background:#111;color:#fff;display:grid;place-items:center;font-size:13px}}
.photo.enc{{background:#1e3a5f}}
ul{{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px}}
</style>
<h1>Sanitized copy</h1>
<p>Assisted redaction with human approval. Not guaranteed anonymisation.</p>
{body}
<h2>Images</h2>
{gallery or "<p>None attached.</p>"}
<h2>Toggles used</h2>
<ul>{toggle_rows}</ul>
</html>
"""
