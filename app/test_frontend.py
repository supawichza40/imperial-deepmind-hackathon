"""Static frontend contracts. No browser. Unittest discover picks this up."""

import unittest
from pathlib import Path

APP = Path(__file__).resolve().parent
STATIC = APP / "static"


def all_hidden(toggles, spans):
    types = {}
    for span in spans or []:
        if span and span.get("type"):
            types[span["type"]] = 1
    keys = list(types)
    if not keys:
        return False
    return all((toggles.get(t) or "keep") != "keep" for t in keys)


class PageMarkupTests(unittest.TestCase):
    def test_vault_html_has_pipeline_root_and_nav(self):
        html = (STATIC / "vault" / "index.html").read_text(encoding="utf-8")
        self.assertIn('name="viewport"', html)
        self.assertIn('id="pgp-root"', html)
        self.assertIn("PrivacyGatePipeline.init", html)
        self.assertIn('href="/privacy-export/"', html)
        self.assertNotIn("PrivacyVault.mount(", html)

    def test_export_html_has_pipeline_root_and_nav(self):
        html = (STATIC / "privacy-export" / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="slot"', html)
        self.assertIn("PrivacyGatePipeline.init", html)
        self.assertIn('href="/vault/"', html)

    def test_theme_html_shares_page_shell(self):
        html = (STATIC / "theme" / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="pg-page"', html)
        self.assertIn('class="pg-nav"', html)


class PipelineContractTests(unittest.TestCase):
    def test_all_hidden_blocks_when_every_detected_type_is_hidden(self):
        spans = [{"type": "name"}, {"type": "email"}]
        self.assertTrue(all_hidden({"name": "blacklabel", "email": "encrypt"}, spans))
        self.assertFalse(all_hidden({"name": "keep", "email": "blacklabel"}, spans))
        self.assertFalse(all_hidden({}, []))

    def test_pipeline_source_matches_fr26_contract(self):
        src = (STATIC / "privacy-export" / "pipeline.js").read_text(encoding="utf-8")
        self.assertIn("function allHidden", src)
        self.assertIn('id="pgp-send"', src)
        self.assertIn("sendBtn.disabled = true", src)
        self.assertIn("Every marked field is hidden", src)


class ButtonIdTests(unittest.TestCase):
    def test_export_action_ids_exist(self):
        src = (STATIC / "privacy-export" / "privacy-export.js").read_text(encoding="utf-8")
        for button_id in ("pg-html", "pg-share", "pg-txt", "pg-json", "pg-pass"):
            self.assertIn(button_id, src)
        self.assertIn('window.location.href = "/vault/"', src)

    def test_vault_action_ids_exist(self):
        src = (STATIC / "vault" / "vault.js").read_text(encoding="utf-8")
        for button_id in ("btn-dl", "btn-share", "btn-lock", "btn-del", "do-lk", "do-un", "mint", "lk-err"):
            self.assertIn(button_id, src)


class MobileCssTests(unittest.TestCase):
    def test_shared_shell_and_mobile_breakpoint(self):
        components = (STATIC / "theme" / "components.css").read_text(encoding="utf-8")
        export_css = (STATIC / "privacy-export" / "privacy-export.css").read_text(encoding="utf-8")
        self.assertIn(".pg-page", components)
        self.assertIn(".pg-nav", components)
        self.assertIn("@media (max-width: 760px)", components)
        self.assertIn("@media (max-width: 760px)", export_css)
        self.assertIn("safe-area-inset-top", components)
        self.assertIn("privacy-gate-v3", (STATIC / "service-worker.js").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
