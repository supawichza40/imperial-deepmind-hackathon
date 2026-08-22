"""PDF text extraction. No OCR."""

from __future__ import annotations

import base64
import unittest

from app.extract_pdf import extract_pdf_text


def pdf_with_text(text: str) -> bytes:
    safe = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 12 Tf 50 700 Td ({safe}) Tj ET\n".encode("latin-1", "replace")
    objects = [
        b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n",
        b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n",
        (
            b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>endobj\n"
        ),
        b"4 0 obj<< /Length " + str(len(stream)).encode("ascii") + b" >>stream\n"
        + stream
        + b"endstream\nendobj\n",
        b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n",
    ]
    header = b"%PDF-1.4\n"
    body = b"".join(objects)
    positions = []
    acc = len(header)
    for obj in objects:
        positions.append(acc)
        acc += len(obj)
    xref = b"xref\n0 6\n0000000000 65535 f \n" + "".join(
        f"{pos:010d} 00000 n \n" for pos in positions
    ).encode("ascii")
    startxref = len(header) + len(body)
    trailer = (
        f"trailer<< /Size 6 /Root 1 0 R >>\nstartxref\n{startxref}\n%%EOF\n"
    ).encode("ascii")
    return header + body + xref + trailer


class ExtractPdfTests(unittest.TestCase):
    def test_reads_selectable_text(self):
        raw = pdf_with_text("A. Okafor NI QQ123456C")
        text, pages = extract_pdf_text(raw)
        self.assertEqual(pages, 1)
        self.assertIn("Okafor", text)
        self.assertIn("QQ123456C", text)

    def test_rejects_non_pdf(self):
        with self.assertRaises(ValueError):
            extract_pdf_text(b"not a pdf")

    def test_rejects_empty_page(self):
        from io import BytesIO

        from pypdf import PdfWriter

        buf = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        writer.write(buf)
        with self.assertRaises(ValueError) as ctx:
            extract_pdf_text(buf.getvalue())
        self.assertIn("selectable text", str(ctx.exception))


class ExtractApiTests(unittest.TestCase):
    def test_post_extract_returns_text(self):
        from fastapi.testclient import TestClient

        from app.api.main import app

        raw = pdf_with_text("Payslip for A. Okafor")
        client = TestClient(app)
        response = client.post(
            "/api/extract",
            json={"filename": "payslip.pdf", "bytes_b64": base64.b64encode(raw).decode("ascii")},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Okafor", data["text"])
        self.assertEqual(data["pages"], 1)

    def test_post_extract_rejects_garbage(self):
        from fastapi.testclient import TestClient

        from app.api.main import app

        client = TestClient(app)
        response = client.post(
            "/api/extract",
            json={"filename": "nope.pdf", "bytes_b64": base64.b64encode(b"hello").decode("ascii")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())


if __name__ == "__main__":
    unittest.main()
