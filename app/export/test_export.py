import json
import unittest
from pathlib import Path
import sys
import zipfile
from io import BytesIO

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.export import apply_export, build_zip_bytes, unlock_vault
from app.export.fields import BLACKLABEL, ENCRYPT, KEEP
from app.export.sample import SAMPLE_IMAGES, SAMPLE_SPANS, SAMPLE_TEXT


class ExportTests(unittest.TestCase):
    def test_blacklabel_hides_address_keeps_pay(self):
        result = apply_export(
            SAMPLE_TEXT,
            SAMPLE_SPANS,
            toggles={
                "address": BLACKLABEL,
                "name": KEEP,
                "ni_number": KEEP,
                "account_number": KEEP,
                "email": KEEP,
                "phone": KEEP,
                "date_of_birth": KEEP,
                "signature": KEEP,
                "personal_image": KEEP,
            },
        )
        self.assertNotIn("14 Pelham St, SW7", result.text)
        self.assertIn("£2,840.00", result.text)
        self.assertIn("█", result.text)

    def test_encrypt_requires_passphrase(self):
        with self.assertRaises(ValueError):
            apply_export(
                SAMPLE_TEXT,
                SAMPLE_SPANS,
                toggles={"ni_number": ENCRYPT},
            )

    def test_encrypt_round_trip(self):
        result = apply_export(
            SAMPLE_TEXT,
            SAMPLE_SPANS,
            toggles={
                "ni_number": ENCRYPT,
                "name": KEEP,
                "address": KEEP,
                "account_number": KEEP,
                "email": KEEP,
                "phone": KEEP,
                "date_of_birth": KEEP,
                "signature": KEEP,
                "personal_image": KEEP,
            },
            passphrase="gate-demo",
        )
        self.assertNotIn("QQ123456C", result.text)
        self.assertIn("ENCRYPTED", result.text)
        self.assertIsNotNone(result.vault)
        opened = unlock_vault(result.vault, "gate-demo")
        ni = next(item for item in opened if item["type"] == "ni_number")
        self.assertEqual(ni["value"], "QQ123456C")

    def test_zip_contains_sanitized_and_audit(self):
        data, result = build_zip_bytes(
            SAMPLE_TEXT,
            SAMPLE_SPANS,
            toggles={"name": BLACKLABEL, "signature": BLACKLABEL, "personal_image": BLACKLABEL},
            images=SAMPLE_IMAGES,
            passphrase=None,
            document_name="payslip",
        )
        zf = zipfile.ZipFile(BytesIO(data))
        names = zf.namelist()
        self.assertTrue(any(n.endswith("sanitized.txt") for n in names))
        self.assertTrue(any(n.endswith("audit.json") for n in names))
        audit = json.loads(
            zf.read(next(n for n in names if n.endswith("audit.json")))
        )
        self.assertTrue(any(e["type"] == "name" for e in audit))
        self.assertIsNone(result.vault)


if __name__ == "__main__":
    unittest.main()
