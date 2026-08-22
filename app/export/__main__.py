"""Write a zip from the sample payslip, or from JSON on stdin."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pack import build_zip_bytes
from .sample import SAMPLE_IMAGES, SAMPLE_SPANS, SAMPLE_TEXT


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Privacy Gate download export")
    p.add_argument("--out", default="privacy-gate-export.zip")
    p.add_argument("--passphrase", default="")
    p.add_argument("--from-json", help="payload JSON {text, spans, toggles, images}")
    p.add_argument("--demo", action="store_true", help="use the invented payslip")
    args = p.parse_args(argv)

    if args.from_json:
        payload = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
    elif args.demo:
        payload = {
            "text": SAMPLE_TEXT,
            "spans": SAMPLE_SPANS,
            "images": SAMPLE_IMAGES,
            "toggles": {
                "name": "blacklabel",
                "address": "blacklabel",
                "ni_number": "encrypt",
                "account_number": "encrypt",
                "email": "blacklabel",
                "phone": "keep",
                "date_of_birth": "blacklabel",
                "signature": "blacklabel",
                "personal_image": "blacklabel",
            },
            "passphrase": args.passphrase or "gate-demo",
            "document_name": "payslip",
        }
    else:
        print("pass --demo or --from-json", file=sys.stderr)
        return 2

    data, result = build_zip_bytes(
        text=payload["text"],
        spans=payload.get("spans") or [],
        toggles=payload.get("toggles"),
        images=payload.get("images"),
        passphrase=payload.get("passphrase") or args.passphrase or None,
        document_name=payload.get("document_name") or "document",
    )
    Path(args.out).write_bytes(data)
    print(f"wrote {args.out} ({len(data)} bytes)")
    print(f"audit entries: {len(result.audit)}")
    print(f"vault: {'yes' if result.vault else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
