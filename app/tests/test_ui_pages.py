"""Static pages that the FastAPI app actually serves."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.main import app

STATIC = Path(__file__).resolve().parents[1] / "static"

client = TestClient(app)


@pytest.mark.parametrize("path", ["/vault/", "/privacy-export/", "/theme/"])
def test_page_has_viewport_and_shared_nav(path):
    response = client.get(path)
    assert response.status_code == 200
    html = response.text
    assert 'name="viewport"' in html
    assert 'content="width=device-width, initial-scale=1"' in html
    assert 'class="pg-top"' in html
    assert 'class="pg-nav"' in html
    assert 'href="/vault/"' in html
    assert 'href="/privacy-export/"' in html


def test_vault_page_starts_pipeline_after_scripts():
    html = client.get("/vault/").text
    assert "pipeline.js" in html
    assert "PrivacyGatePipeline.init" in html
    assert 'id="pgp-root"' in html
    assert 'id="vault"' in html
    assert "PrivacyVault.mount(" not in html
    assert "detectAndPublish" not in html


def test_export_page_starts_pipeline():
    html = client.get("/privacy-export/").text
    assert "pipeline.js" in html
    assert "PrivacyGatePipeline.init" in html
    assert 'id="slot"' in html
    assert 'id="pgp-root"' in html
    assert 'class="pgp-flow"' in html


def test_pipeline_js_wires_send_and_fr26():
    src = (STATIC / "privacy-export" / "pipeline.js").read_text(encoding="utf-8")
    assert "function allHidden" in src
    assert 'id="pgp-send"' in src
    assert 'aria-live="polite"' in src
    assert "sendBtn.disabled = true" in src
    assert "Every marked field is hidden" in src
    assert "initVaultPage" in src
    assert 'querySelector("#vault")' in src
    assert 'querySelector("#slot")' in src
    assert 'id="pgp-file"' in src
    assert 'id="pgp-browse"' in src
    assert 'id="pgp-paste"' in src
    assert "readLocalFile" in src
    assert "pgp-leaving" in src


def test_share_button_opens_vault_when_off_vault():
    src = (STATIC / "privacy-export" / "privacy-export.js").read_text(encoding="utf-8")
    assert 'window.location.href = "/vault/"' in src
    assert "pg-share" in src
    assert "pg-html" in src
    assert "pg-txt" in src
    assert "pg-json" in src


def test_lock_modal_rejects_empty_passphrase():
    src = (STATIC / "vault" / "vault.js").read_text(encoding="utf-8")
    assert "lk-err" in src
    assert "Type a passphrase to lock this folder." in src
    assert "Type the folder passphrase." in src
    assert "btn-share" in src
    assert "btn-dl" in src
    assert "btn-lock" in src
    assert "btn-add-file" in src


def test_mobile_css_stacks_rows_and_wraps_audit():
    export_css = (STATIC / "privacy-export" / "privacy-export.css").read_text(encoding="utf-8")
    pipeline_css = (STATIC / "privacy-export" / "pipeline.css").read_text(encoding="utf-8")
    components = (STATIC / "theme" / "components.css").read_text(encoding="utf-8")
    vault_css = (STATIC / "vault" / "vault.css").read_text(encoding="utf-8")
    assert "@media (max-width: 760px)" in export_css
    assert "grid-template-columns: 44px minmax(0, 1fr)" in export_css
    assert ".pgp-audit-wrap" in pipeline_css
    assert "overflow-x: auto" in pipeline_css
    assert ".pg-page" in components
    assert ".pg-nav" in components
    assert "safe-area-inset-top" in components
    assert "overscroll-behavior: contain" in vault_css
    assert "100dvh" in vault_css
