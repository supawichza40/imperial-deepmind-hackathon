import json
import sys
import unittest
import zipfile
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.export import apply_export, build_zip_bytes, unlock_vault
from app.export.crypto import decrypt_blob, derive_key, encrypt_blob, encrypt_text, new_salt
from app.export.fields import BLACKLABEL, ENCRYPT, KEEP, default_toggles, label_for
from app.export.redact import Span
from app.export.sample import SAMPLE_IMAGES, SAMPLE_SPANS, SAMPLE_TEXT


KEEP_ALL = {t: KEEP for t in (
    "name", "address", "ni_number", "account_number", "email",
    "phone", "date_of_birth", "signature", "personal_image",
)}


def _toggles(**overrides):
    out = dict(KEEP_ALL)
    out.update(overrides)
    return out


class SampleIntegrityTests(unittest.TestCase):
    def test_every_text_span_matches_the_document(self):
        for span in SAMPLE_SPANS:
            if span["end"] <= span["start"]:
                continue
            slice_ = SAMPLE_TEXT[span["start"]:span["end"]]
            self.assertEqual(slice_, span["value"], span["id"])

    def test_name_and_signature_are_different_occurrences(self):
        name = next(s for s in SAMPLE_SPANS if s["id"] == "name-1")
        sig = next(s for s in SAMPLE_SPANS if s["id"] == "sig-text")
        self.assertLess(name["end"], sig["start"])


class FieldTests(unittest.TestCase):
    def test_unknown_type_gets_a_readable_label(self):
        self.assertEqual(label_for("medical_note"), "Medical Note")

    def test_default_toggles_include_unknown_present_types(self):
        toggles = default_toggles(["name", "medical_note"])
        self.assertEqual(toggles["name"], BLACKLABEL)
        self.assertEqual(toggles["medical_note"], KEEP)


class CryptoTests(unittest.TestCase):
    def test_text_round_trip(self):
        key = derive_key("phrase", new_salt())
        item = encrypt_text(key, "QQ123456C")
        from app.export.crypto import decrypt_text
        self.assertEqual(decrypt_text(key, item), "QQ123456C")

    def test_blob_round_trip(self):
        key = derive_key("phrase", new_salt())
        item = encrypt_blob(key, b"svg-bytes")
        self.assertEqual(decrypt_blob(key, item), b"svg-bytes")

    def test_wrong_key_cannot_read(self):
        salt = new_salt()
        item = encrypt_text(derive_key("a", salt), "secret")
        from app.export.crypto import decrypt_text
        with self.assertRaises(Exception):
            decrypt_text(derive_key("b", salt), item)

    def test_empty_passphrase_is_rejected(self):
        with self.assertRaises(ValueError):
            derive_key("", new_salt())


class RedactTests(unittest.TestCase):
    def test_blacklabel_does_not_touch_pay_figures(self):
        result = apply_export(SAMPLE_TEXT, SAMPLE_SPANS, toggles=_toggles(address=BLACKLABEL))
        self.assertNotIn("14 Pelham St, SW7", result.text)
        self.assertIn("£2,840.00", result.text)
        self.assertIn("£412.60", result.text)

    def test_only_signature_blacklabel_keeps_the_staff_photo(self):
        result = apply_export(
            SAMPLE_TEXT,
            SAMPLE_SPANS,
            toggles=_toggles(signature=BLACKLABEL),
            images=SAMPLE_IMAGES,
        )
        photo = next(img for img in result.images if img["id"] == "staff-photo")
        sig = next(img for img in result.images if img["id"] == "wet-signature")
        self.assertTrue(photo.get("data_url"))
        self.assertFalse(photo.get("blacklabeled"))
        self.assertTrue(sig.get("blacklabeled"))
        self.assertFalse(sig.get("data_url"))

    def test_encrypt_round_trip_and_wrong_phrase_fails(self):
        result = apply_export(
            SAMPLE_TEXT,
            SAMPLE_SPANS,
            toggles=_toggles(ni_number=ENCRYPT, email=ENCRYPT),
            passphrase="gate-demo",
        )
        self.assertNotIn("QQ123456C", result.text)
        self.assertNotIn("a.okafor@example.com", result.text)
        opened = unlock_vault(result.vault, "gate-demo")
        types = {item["type"]: item["value"] for item in opened if item["type"] in ("ni_number", "email")}
        self.assertEqual(types["ni_number"], "QQ123456C")
        self.assertEqual(types["email"], "a.okafor@example.com")
        with self.assertRaises(Exception):
            unlock_vault(result.vault, "wrong")

    def test_html_escapes_angle_brackets(self):
        text = "Name: <script>alert(1)</script>"
        spans = [{"type": "name", "start": 6, "end": len(text), "value": "<script>alert(1)</script>"}]
        result = apply_export(text, spans, toggles={"name": KEEP})
        self.assertIn("&lt;script&gt;", result.html)
        self.assertNotIn("<script>", result.html)

    def test_overlapping_spans_keep_the_earlier_span_only(self):
        text = "ABCDEFGHIJ"
        spans = [
            {"id": "a", "type": "name", "start": 0, "end": 6, "value": "ABCDEF"},
            {"id": "b", "type": "address", "start": 4, "end": 10, "value": "EFGHIJ"},
        ]
        result = apply_export(text, spans, toggles=_toggles(name=BLACKLABEL, address=BLACKLABEL))
        self.assertNotIn("ABCDEF", result.text)
        self.assertIn("GHIJ", result.text)

    def test_keep_all_leaves_the_sample_intact(self):
        result = apply_export(SAMPLE_TEXT, SAMPLE_SPANS, toggles=_toggles())
        self.assertIn("QQ123456C", result.text)
        self.assertIn("A. Okafor", result.text)
        self.assertIn("14 Pelham St, SW7", result.text)

    def test_empty_span_list_returns_the_original_text(self):
        result = apply_export("hello", [], toggles={})
        self.assertEqual(result.text, "hello")

    def test_adjacent_spans_both_apply(self):
        text = "AAABBB"
        spans = [
            {"type": "name", "start": 0, "end": 3, "value": "AAA"},
            {"type": "email", "start": 3, "end": 6, "value": "BBB"},
        ]
        result = apply_export(text, spans, toggles=_toggles(name=BLACKLABEL, email=BLACKLABEL))
        self.assertNotIn("AAA", result.text)
        self.assertNotIn("BBB", result.text)

    def test_whitespace_passphrase_is_rejected_for_encrypt(self):
        with self.assertRaises(ValueError):
            apply_export(
                SAMPLE_TEXT,
                SAMPLE_SPANS,
                toggles=_toggles(ni_number=ENCRYPT),
                passphrase="   ",
            )

    def test_zip_contains_sanitized_text_and_audit(self):
        data, result = build_zip_bytes(
            SAMPLE_TEXT,
            SAMPLE_SPANS,
            toggles=_toggles(name=BLACKLABEL, signature=BLACKLABEL, personal_image=BLACKLABEL),
            images=SAMPLE_IMAGES,
            document_name="payslip",
        )
        zf = zipfile.ZipFile(BytesIO(data))
        names = zf.namelist()
        self.assertTrue(any(n.endswith("sanitized.txt") for n in names))
        self.assertTrue(any(n.endswith("audit.json") for n in names))
        audit = json.loads(zf.read(next(n for n in names if n.endswith("audit.json"))))
        self.assertTrue(any(e["type"] == "name" for e in audit))
        self.assertIsNone(result.vault)

    def test_encrypted_zip_does_not_contain_plaintext_ni(self):
        data, _result = build_zip_bytes(
            SAMPLE_TEXT,
            SAMPLE_SPANS,
            toggles=_toggles(ni_number=ENCRYPT),
            passphrase="gate-demo",
            document_name="payslip",
        )
        blob = data.decode("latin-1")
        self.assertNotIn("QQ123456C", blob)

    def test_invalid_span_is_skipped(self):
        text = "hello"
        spans = [
            {"type": "name", "start": 9, "end": 12, "value": "nope"},
            {"type": "email", "start": 0, "end": 5, "value": "hello"},
        ]
        result = apply_export(text, spans, toggles=_toggles(email=BLACKLABEL, name=BLACKLABEL))
        self.assertNotIn("hello", result.text)

    def test_span_from_dict_rejects_backwards_range(self):
        with self.assertRaises(ValueError):
            Span.from_dict({"type": "name", "start": 9, "end": 2}, 0)

    def test_zip_omits_original_when_photo_is_blacklabeled(self):
        data, result = build_zip_bytes(
            SAMPLE_TEXT,
            SAMPLE_SPANS,
            toggles=_toggles(personal_image=BLACKLABEL, signature=KEEP, name=KEEP),
            images=SAMPLE_IMAGES,
            document_name="payslip",
        )
        zf = zipfile.ZipFile(BytesIO(data))
        names = zf.namelist()
        self.assertTrue(any("staff-photo.BLACKLABELED.txt" in n for n in names))
        self.assertFalse(any("staff-photo.url.txt" in n for n in names))
        html = zf.read(next(n for n in names if n.endswith("sanitized.html"))).decode("utf-8")
        self.assertIn("photo blacklabeled", html)
        self.assertNotIn("STAFF PHOTO", html)
        self.assertIsNone(result.vault)


class ZipSafetyTests(unittest.TestCase):
    def test_html_page_escapes_field_type_in_title(self):
        from app.export.pack import _html_page
        page = _html_page(
            "<pre>x</pre>",
            [{"id": "i", "data_url": "data:image/png;base64,xx", "boxes": [
                {"action": "blacklabel", "type": '"><img src=x>', "bbox": [0, 0, 1, 1]}
            ]}],
            {"name": "keep"},
        )
        self.assertNotIn('"><img src=x>', page)
        self.assertIn("&quot;", page)

    def test_zip_paths_cannot_escape_the_folder(self):
        data, _result = build_zip_bytes(
            "hello",
            [],
            document_name="../evil/name",
        )
        zf = zipfile.ZipFile(BytesIO(data))
        for name in zf.namelist():
            self.assertNotIn("..", name)
            self.assertNotIn("\\", name)
            self.assertTrue(name.startswith("privacy-gate-evil-name-"))


if __name__ == "__main__":
    unittest.main()
