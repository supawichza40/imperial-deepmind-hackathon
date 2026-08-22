import gzip
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.access.share import KEY_ALPHABET, new_creator_key, normalize_key
from app.access.transfer import pack_file, unpack_file
from app.export.redact import apply_export
from app.export.fields import BLACKLABEL, KEEP
from app.export.sample import SAMPLE_SPANS, SAMPLE_TEXT


KEEP_ALL = {
    "name": KEEP,
    "address": KEEP,
    "ni_number": KEEP,
    "account_number": KEEP,
    "email": KEEP,
    "phone": KEEP,
    "date_of_birth": KEEP,
    "signature": KEEP,
    "personal_image": KEEP,
}


class KeyShapeTests(unittest.TestCase):
    def test_normalize_strips_punctuation_and_case(self):
        self.assertEqual(normalize_key("ab3d-k7pq"), "AB3DK7PQ")
        self.assertEqual(normalize_key("  ab 3d  "), "AB3D")
        self.assertEqual(normalize_key(""), "")
        self.assertEqual(normalize_key(None), "")

    def test_new_creator_key_is_eight_safe_chars(self):
        key = new_creator_key()
        self.assertRegex(key, r"^[A-Z0-9]{4}-[A-Z0-9]{4}$")
        compact = key.replace("-", "")
        self.assertTrue(all(ch in KEY_ALPHABET for ch in compact))
        self.assertNotIn("O", compact)
        self.assertNotIn("I", compact)
        self.assertNotIn("0", compact)
        self.assertNotIn("1", compact)


class TransferTests(unittest.TestCase):
    def test_round_trip_without_a_key(self):
        payload = pack_file(name="July payslip", text=SAMPLE_TEXT, perm="download", now=1000)
        got = unpack_file(payload, now=1000)
        self.assertEqual(got["name"], "July payslip")
        self.assertEqual(got["text"], SAMPLE_TEXT)
        self.assertEqual(got["perm"], "download")
        self.assertFalse(got["needs_key"])

    def test_view_perm_round_trip(self):
        payload = pack_file(name="note", text="hello", perm="view", now=1000)
        got = unpack_file(payload, now=1000)
        self.assertEqual(got["perm"], "view")

    def test_unicode_and_empty_body_round_trip(self):
        payload = pack_file(name="fiche de paie", text="Net £2,427.40\n", now=50)
        got = unpack_file(payload, now=50)
        self.assertEqual(got["name"], "fiche de paie")
        self.assertEqual(got["text"], "Net £2,427.40\n")
        empty = pack_file(name="blank", text="", now=50)
        self.assertEqual(unpack_file(empty, now=50)["text"], "")

    def test_key_gate_on_a_transferred_file(self):
        payload = pack_file(
            name="July payslip",
            text=SAMPLE_TEXT,
            perm="view",
            creator_key="AB3D-K7PQ",
            now=1000,
        )
        with self.assertRaises(ValueError) as ctx:
            unpack_file(payload, now=1000)
        self.assertIn("creator key required", str(ctx.exception))
        with self.assertRaises(ValueError):
            unpack_file(payload, creator_key="NOPE-NOPE", now=1000)
        got = unpack_file(payload, creator_key="ab3d k7pq", now=1000)
        self.assertEqual(got["text"], SAMPLE_TEXT)
        self.assertEqual(got["perm"], "view")
        self.assertTrue(got["needs_key"])

    def test_blank_creator_key_does_not_lock_the_file(self):
        payload = pack_file(name="open", text="visible", creator_key="   ", now=1000)
        got = unpack_file(payload, now=1000)
        self.assertFalse(got["needs_key"])
        self.assertEqual(got["text"], "visible")

    def test_expired_transfer_is_rejected(self):
        payload = pack_file(name="x", text="hello", ttl_seconds=1, now=1000)
        with self.assertRaises(ValueError) as ctx:
            unpack_file(payload, now=2000)
        self.assertIn("expired", str(ctx.exception))

    def test_payload_does_not_contain_plaintext_when_keyed(self):
        payload = pack_file(
            name="July payslip",
            text="QQ123456C secret",
            creator_key="AB3D-K7PQ",
            now=1000,
        )
        self.assertNotIn("QQ123456C", payload)
        self.assertNotIn("secret", payload)
        self.assertNotIn("July payslip", payload)

    def test_two_keyed_packs_are_not_identical(self):
        a = pack_file(name="n", text="same", creator_key="AB3D-K7PQ", now=1000)
        b = pack_file(name="n", text="same", creator_key="AB3D-K7PQ", now=1000)
        self.assertNotEqual(a, b)

    def test_payload_is_url_safe(self):
        payload = pack_file(name="July payslip", text=SAMPLE_TEXT, now=1000)
        self.assertNotIn("+", payload)
        self.assertNotIn("/", payload)
        self.assertNotIn("=", payload)
        self.assertNotIn(" ", payload)

    def test_qr_url_fits_a_version_40_code(self):
        redacted = apply_export(
            SAMPLE_TEXT,
            SAMPLE_SPANS,
            toggles={**KEEP_ALL, "name": BLACKLABEL, "ni_number": BLACKLABEL, "signature": BLACKLABEL},
        )
        payload = pack_file(name="July payslip", text=redacted.text, perm="download", now=1000)
        url = "http://192.168.1.12:8765/vault/index.html#t=" + payload
        self.assertLess(len(url.encode("utf-8")), 2900)
        self.assertNotIn("QQ123456C", url)
        self.assertNotIn("QQ123456C", redacted.text)
        self.assertNotIn("A. Okafor", redacted.text)

    def test_bad_perm_is_rejected(self):
        with self.assertRaises(ValueError):
            pack_file(name="x", text="y", perm="admin")

    def test_garbage_payload_is_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            unpack_file("not-a-payload")
        self.assertIn("bad transfer payload", str(ctx.exception))

    def test_tampered_gzip_is_rejected(self):
        payload = pack_file(name="x", text="hello", now=1000)
        flipped = ("A" if payload[0] != "A" else "B") + payload[1:]
        with self.assertRaises(ValueError):
            unpack_file(flipped, now=1000)

    def test_json_without_file_fields_is_rejected(self):
        from app.access.transfer import _b64
        raw = json.dumps({"v": 1, "x": 9_999_999_999}).encode("utf-8")
        payload = _b64(gzip.compress(raw, 9))
        with self.assertRaises(ValueError) as ctx:
            unpack_file(payload, now=1000)
        self.assertIn("bad transfer payload", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
