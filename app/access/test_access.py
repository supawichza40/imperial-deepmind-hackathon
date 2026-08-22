import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.access import Vault, totp, verify_totp
from app.access.acl import Acl


class AccessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.v = Vault(hmac_secret=b"test-secret-32-bytes-long-ok!!")
        self.v.register("owner@local")
        self.v.register("guest@local")

    def test_totp_round_trip(self) -> None:
        secret = self.v.actors["owner@local"].totp_secret
        code = totp(secret, at=1_700_000_000)
        self.assertTrue(verify_totp(secret, code, at=1_700_000_000))
        self.assertFalse(verify_totp(secret, "000000", at=1_700_000_000))

    def test_viewer_cannot_download(self) -> None:
        folder = self.v.add_folder("owner@local", "Inbox")
        folder.acl.grant("owner@local", "guest@local", "viewer")
        doc = self.v.add_doc("owner@local", folder.id, "payslip.txt", "secret")
        with self.assertRaises(PermissionError):
            self.v.download("guest@local", doc.id)

    def test_share_link_download(self) -> None:
        folder = self.v.add_folder("owner@local", "Inbox")
        doc = self.v.add_doc("owner@local", folder.id, "payslip.txt", "ok")
        token = self.v.share_link("owner@local", doc.id, perm="download")
        perm, opened = self.v.open_share(token)
        self.assertEqual(perm, "download")
        self.assertEqual(opened.text, "ok")

    def test_locked_folder_blocks_list(self) -> None:
        folder = self.v.add_folder("owner@local", "Identity")
        self.v.lock_folder("owner@local", folder.id, "lock-phrase")
        with self.assertRaises(PermissionError):
            self.v.list_docs("owner@local", folder.id)
        self.v.unlock_folder("owner@local", folder.id, "lock-phrase")
        self.assertEqual(self.v.list_docs("owner@local", folder.id), [])

    def test_delete_needs_name_and_totp(self) -> None:
        folder = self.v.add_folder("owner@local", "Inbox")
        secret = self.v.actors["owner@local"].totp_secret
        with self.assertRaises(PermissionError):
            self.v.delete_folder("owner@local", folder.id, "Wrong", totp(secret))
        with self.assertRaises(PermissionError):
            self.v.delete_folder("owner@local", folder.id, "Inbox", "000000")
        self.v.delete_folder("owner@local", folder.id, "Inbox", totp(secret))
        self.assertNotIn(folder.id, self.v.folders)

    def test_acl_owner_cannot_be_removed(self) -> None:
        acl = Acl(owner="owner@local")
        with self.assertRaises(ValueError):
            acl.revoke("owner@local", "owner@local")


if __name__ == "__main__":
    unittest.main()
