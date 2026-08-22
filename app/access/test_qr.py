"""QR encoder checks. Needs Node on PATH."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.access.transfer import pack_file
from app.export.sample import SAMPLE_TEXT

VAULT = ROOT / "app" / "static" / "vault"
NODE_SCRIPT = r"""
const fs = require("fs");
const vm = require("vm");
const vault = process.env.PG_VAULT;
const url = process.env.PG_QR_URL;
const ctx = {
  console,
  Uint8Array,
  Array,
  Math,
  Number,
  RangeError,
  Error,
  parseInt,
  isNaN
};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(vault + "/qrcodegen.js", "utf8"), ctx);
vm.runInContext(fs.readFileSync(vault + "/qr.js", "utf8"), ctx);
if (!ctx.PrivacyQr || !ctx.qrcodegen) {
  throw new Error("QR libraries did not load");
}
const svg = ctx.PrivacyQr.svg(url);
const empty = ctx.PrivacyQr.svg("");
const qr = ctx.qrcodegen.QrCode.encodeText(url, ctx.qrcodegen.QrCode.Ecc.LOW);
const out = {
  ok: svg.indexOf("<svg") === 0 && svg.indexOf("</svg>") !== -1,
  hasLabel: svg.indexOf("QR code that carries the sanitised file") !== -1,
  hasInk: svg.indexOf("#111111") !== -1,
  emptyIsBlank: empty === "",
  rects: (svg.match(/<rect /g) || []).length,
  size: qr.size
};
process.stdout.write(JSON.stringify(out));
"""


@unittest.skipUnless(shutil.which("node"), "node is not on PATH")
class QrEncodeTests(unittest.TestCase):
    def test_encoder_draws_an_svg_for_a_transfer_url(self):
        payload = pack_file(name="July payslip", text=SAMPLE_TEXT, perm="download", now=1000)
        url = "http://192.168.1.12:8765/vault/index.html#t=" + payload
        env = os.environ.copy()
        env["PG_VAULT"] = str(VAULT)
        env["PG_QR_URL"] = url
        proc = subprocess.run(
            ["node", "-e", NODE_SCRIPT],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=20,
            env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["ok"])
        self.assertTrue(data["hasLabel"])
        self.assertTrue(data["hasInk"])
        self.assertTrue(data["emptyIsBlank"])
        self.assertGreater(data["rects"], 200)
        self.assertGreaterEqual(data["size"], 21)
        self.assertLessEqual(data["size"], 177)

    def test_encoder_files_are_present(self):
        self.assertTrue((VAULT / "qrcodegen.js").is_file())
        self.assertTrue((VAULT / "qr.js").is_file())
        header = (VAULT / "qrcodegen.js").read_text(encoding="utf-8")[:400]
        self.assertIn("Project Nayuki", header)
        self.assertIn("MIT License", header)


if __name__ == "__main__":
    unittest.main()
