import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.access.transfer import pack_file, unpack_file
from app.export.sample import SAMPLE_TEXT


class TransferTests(unittest.TestCase):
    def test_round_trip_without_a_key(self):
        payload = pack_file(name="July payslip", text=SAMPLE_TEXT, perm="download", now=1000)
        got = unpack_file(payload, now=1000)
        self.assertEqual(got["name"], "July payslip")
        self.assertEqual(got["text"], SAMPLE_TEXT)
        self.assertEqual(got["perm"], "download")
        self.assertFalse(got["needs_key"])

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


if __name__ == "__main__":
    unittest.main()
