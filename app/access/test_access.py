import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.access import Vault, totp, verify_totp
from app.access.acl import Acl, inherit
from app.access.share import mint as mint_share
from app.access.share import open_token as open_share


class TotpTests(unittest.TestCase):
    def test_accepts_spaces_in_the_code(self):
        secret = "JBSWY3DPEHPK3PXP"
        code = totp(secret, at=1_700_000_030)
        self.assertTrue(verify_totp(secret, f"{code[:3]} {code[3:]}", at=1_700_000_030))

    def test_rejects_short_codes(self):
        self.assertFalse(verify_totp("JBSWY3DPEHPK3PXP", "12", at=1_700_000_030))

    def test_window_accepts_previous_step(self):
        secret = "JBSWY3DPEHPK3PXP"
        previous = totp(secret, at=1_700_000_000, offset=-1)
        self.assertTrue(verify_totp(secret, previous, at=1_700_000_000, window=1))
        self.assertFalse(verify_totp(secret, previous, at=1_700_000_000, window=0))


class AclTests(unittest.TestCase):
    def test_role_ladder(self):
        acl = Acl(owner="o@x")
        acl.grant("o@x", "v@x", "viewer")
        acl.grant("o@x", "d@x", "downloader")
        acl.grant("o@x", "e@x", "editor")
        acl.grant("o@x", "a@x", "admin")
        self.assertTrue(acl.can("v@x", "view"))
        self.assertFalse(acl.can("v@x", "download"))
        self.assertTrue(acl.can("d@x", "download"))
        self.assertFalse(acl.can("d@x", "share"))
        self.assertTrue(acl.can("e@x", "share"))
        self.assertFalse(acl.can("e@x", "acl"))
        self.assertTrue(acl.can("a@x", "lock"))
        self.assertFalse(acl.can("a@x", "delete"))
        self.assertTrue(acl.can("o@x", "delete"))

    def test_stranger_has_no_access(self):
        acl = Acl(owner="o@x")
        self.assertFalse(acl.can("nope@x", "view"))

    def test_editor_cannot_grant(self):
        acl = Acl(owner="o@x")
        acl.grant("o@x", "e@x", "editor")
        with self.assertRaises(PermissionError):
            acl.grant("e@x", "v@x", "viewer")

    def test_invalid_role_rejected(self):
        acl = Acl(owner="o@x")
        with self.assertRaises(ValueError):
            acl.grant("o@x", "x@x", "superadmin")

    def test_round_trip_dict(self):
        acl = Acl(owner="o@x", members={"a@x": "admin"})
        again = Acl.from_dict(acl.to_dict())
        self.assertEqual(again.owner, "o@x")
        self.assertEqual(again.members["a@x"], "admin")

    def test_inherit_child_wins_on_the_same_email(self):
        parent = Acl(owner="o@x", members={"g@x": "downloader"})
        child = Acl(owner="o@x", members={"g@x": "viewer"})
        merged = inherit(parent, child)
        self.assertEqual(merged.role_of("g@x"), "viewer")
        self.assertFalse(merged.can("g@x", "download"))

    def test_owner_cannot_be_removed(self):
        acl = Acl(owner="owner@local")
        with self.assertRaises(ValueError):
            acl.revoke("owner@local", "owner@local")


class ShareTests(unittest.TestCase):
    def test_tamper_is_rejected(self):
        token = mint_share(b"k" * 32, folder_id="f", doc_id="d", perm="view", actor="o@x")
        last = token[-1]
        bad = token[:-1] + ("A" if last != "A" else "B")
        with self.assertRaises(ValueError):
            open_share(b"k" * 32, bad)

    def test_wrong_secret_is_rejected(self):
        token = mint_share(b"k" * 32, folder_id="f", doc_id="d", perm="download", actor="o@x")
        with self.assertRaises(ValueError):
            open_share(b"z" * 32, token)

    def test_expired_token_is_rejected(self):
        token = mint_share(
            b"k" * 32, folder_id="f", doc_id="d", perm="view", actor="o@x",
            ttl_seconds=1, now=1000,
        )
        with self.assertRaises(ValueError) as ctx:
            open_share(b"k" * 32, token, now=2000)
        self.assertIn("expired", str(ctx.exception))

    def test_bad_perm_is_rejected(self):
        with self.assertRaises(ValueError):
            mint_share(b"k" * 32, folder_id="f", doc_id="d", perm="admin", actor="o@x")

    def test_malformed_token(self):
        with self.assertRaises(ValueError):
            open_share(b"k" * 32, "not-a-token")

    def test_signed_but_empty_json_is_rejected(self):
        import hashlib
        import hmac
        from app.access.share import _b64
        payload = _b64(b"{}")
        sig = _b64(hmac.new(b"k" * 32, payload.encode("ascii"), hashlib.sha256).digest())
        with self.assertRaises(ValueError):
            open_share(b"k" * 32, f"{payload}.{sig}")


class VaultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.v = Vault(hmac_secret=b"test-secret-32-bytes-long-ok!!")
        self.v.register("owner@local")
        self.v.register("guest@local")
        self.v.register("editor@local")

    def test_nested_delete_removes_grandchildren(self):
        root = self.v.add_folder("owner@local", "Root")
        child = self.v.add_folder("owner@local", "Child", parent_id=root.id)
        grand = self.v.add_folder("owner@local", "Grand", parent_id=child.id)
        doc = self.v.add_doc("owner@local", grand.id, "deep.txt", "x")
        self.v.delete_folder("owner@local", root.id, "Root", totp(self.v.actors["owner@local"].totp_secret))
        self.assertNotIn(root.id, self.v.folders)
        self.assertNotIn(child.id, self.v.folders)
        self.assertNotIn(grand.id, self.v.folders)
        self.assertNotIn(doc.id, self.v.docs)

    def test_empty_lock_passphrase_rejected(self):
        folder = self.v.add_folder("owner@local", "Inbox")
        with self.assertRaises(ValueError):
            self.v.lock_folder("owner@local", folder.id, "   ")

    def test_empty_folder_name_rejected(self):
        with self.assertRaises(ValueError):
            self.v.add_folder("owner@local", "  ")

    def test_wrong_lock_passphrase(self):
        folder = self.v.add_folder("owner@local", "Identity")
        self.v.lock_folder("owner@local", folder.id, "right")
        with self.assertRaises(PermissionError):
            self.v.unlock_folder("owner@local", folder.id, "wrong")

    def test_parent_grant_reaches_child(self):
        parent = self.v.add_folder("owner@local", "Parent")
        child = self.v.add_folder("owner@local", "Child", parent_id=parent.id)
        parent.acl.grant("owner@local", "guest@local", "downloader")
        doc = self.v.add_doc("owner@local", child.id, "file.txt", "hello")
        got = self.v.download("guest@local", doc.id)
        self.assertEqual(got.text, "hello")

    def test_editor_cannot_delete(self):
        folder = self.v.add_folder("owner@local", "Inbox")
        folder.acl.grant("owner@local", "editor@local", "editor")
        self.v.register("editor@local")
        with self.assertRaises(PermissionError):
            self.v.delete_folder(
                "editor@local", folder.id, "Inbox",
                totp(self.v.actors["editor@local"].totp_secret),
            )

    def test_viewer_cannot_share(self):
        folder = self.v.add_folder("owner@local", "Inbox")
        folder.acl.grant("owner@local", "guest@local", "viewer")
        doc = self.v.add_doc("owner@local", folder.id, "a.txt", "x")
        with self.assertRaises(PermissionError):
            self.v.share_link("guest@local", doc.id)

    def test_missing_folder(self):
        with self.assertRaises(KeyError):
            self.v.list_docs("owner@local", "nope")

    def test_unregistered_actor_cannot_delete(self):
        folder = self.v.add_folder("owner@local", "Inbox")
        folder.acl.owner = "ghost@local"
        with self.assertRaises(PermissionError):
            self.v.delete_folder("ghost@local", folder.id, "Inbox", "123456")

    def test_totp_round_trip(self):
        secret = self.v.actors["owner@local"].totp_secret
        code = totp(secret, at=1_700_000_000)
        self.assertTrue(verify_totp(secret, code, at=1_700_000_000))
        self.assertFalse(verify_totp(secret, "000000", at=1_700_000_000))

    def test_viewer_cannot_download(self):
        folder = self.v.add_folder("owner@local", "Inbox")
        folder.acl.grant("owner@local", "guest@local", "viewer")
        doc = self.v.add_doc("owner@local", folder.id, "payslip.txt", "secret")
        with self.assertRaises(PermissionError):
            self.v.download("guest@local", doc.id)

    def test_share_link_download(self):
        folder = self.v.add_folder("owner@local", "Inbox")
        doc = self.v.add_doc("owner@local", folder.id, "payslip.txt", "ok")
        token = self.v.share_link("owner@local", doc.id, perm="download")
        perm, opened = self.v.open_share(token)
        self.assertEqual(perm, "download")
        self.assertEqual(opened.text, "ok")

    def test_view_share_still_returns_the_file(self):
        folder = self.v.add_folder("owner@local", "Inbox")
        doc = self.v.add_doc("owner@local", folder.id, "payslip.txt", "ok")
        token = self.v.share_link("owner@local", doc.id, perm="view")
        perm, opened = self.v.open_share(token)
        self.assertEqual(perm, "view")
        self.assertEqual(opened.text, "ok")

    def test_locked_folder_blocks_list(self):
        folder = self.v.add_folder("owner@local", "Identity")
        self.v.lock_folder("owner@local", folder.id, "lock-phrase")
        with self.assertRaises(PermissionError):
            self.v.list_docs("owner@local", folder.id)
        self.v.unlock_folder("owner@local", folder.id, "lock-phrase")
        self.assertEqual(self.v.list_docs("owner@local", folder.id), [])

    def test_delete_needs_name_and_totp(self):
        folder = self.v.add_folder("owner@local", "Inbox")
        secret = self.v.actors["owner@local"].totp_secret
        with self.assertRaises(PermissionError):
            self.v.delete_folder("owner@local", folder.id, "Wrong", totp(secret))
        with self.assertRaises(PermissionError):
            self.v.delete_folder("owner@local", folder.id, "Inbox", "000000")
        self.v.delete_folder("owner@local", folder.id, "Inbox", totp(secret))
        self.assertNotIn(folder.id, self.v.folders)

    def test_parent_lock_blocks_child_write(self):
        parent = self.v.add_folder("owner@local", "Parent")
        child = self.v.add_folder("owner@local", "Child", parent_id=parent.id)
        self.v.lock_folder("owner@local", parent.id, "lock")
        with self.assertRaises(PermissionError):
            self.v.add_doc("owner@local", child.id, "x.txt", "x")

    def test_folder_name_is_stripped(self):
        folder = self.v.add_folder("owner@local", "  Inbox  ")
        self.assertEqual(folder.name, "Inbox")

    def test_admin_can_lock_but_cannot_delete(self):
        folder = self.v.add_folder("owner@local", "Inbox")
        self.v.register("admin@local")
        folder.acl.grant("owner@local", "admin@local", "admin")
        self.v.lock_folder("admin@local", folder.id, "phrase")
        with self.assertRaises(PermissionError):
            self.v.delete_folder(
                "admin@local",
                folder.id,
                "Inbox",
                totp(self.v.actors["admin@local"].totp_secret),
            )

    def test_revoke_removes_access(self):
        folder = self.v.add_folder("owner@local", "Inbox")
        folder.acl.grant("owner@local", "guest@local", "viewer")
        folder.acl.revoke("owner@local", "guest@local")
        with self.assertRaises(PermissionError):
            self.v.list_docs("guest@local", folder.id)


if __name__ == "__main__":
    unittest.main()
