"""Invented payslip used by the export demo. Not real personal data."""

SAMPLE_TEXT = """ACME LTD  —  PAYSLIP
Period: July 2026

Employee: A. Okafor
NI number: QQ123456C
Address: 14 Pelham St, SW7
Email: a.okafor@example.com
Phone: 07700 900123
Account: 4417
Date of birth: 14 Mar 1998

Gross pay: £2,840.00
Tax paid: £412.60
Net pay: £2,427.40

Signature: A. Okafor
"""


def _span(field_type: str, needle: str, nth: int = 1, **extra) -> dict:
    start = -1
    for _ in range(nth):
        start = SAMPLE_TEXT.index(needle, start + 1)
    return {
        "id": extra.pop("id", field_type),
        "type": field_type,
        "start": start,
        "end": start + len(needle),
        "value": needle,
        "kind": extra.pop("kind", "text"),
        **extra,
    }


SAMPLE_SPANS = [
    _span("name", "A. Okafor", id="name-1"),
    _span("ni_number", "QQ123456C"),
    _span("address", "14 Pelham St, SW7"),
    _span("email", "a.okafor@example.com"),
    _span("phone", "07700 900123"),
    _span("account_number", "4417"),
    _span("date_of_birth", "14 Mar 1998"),
    _span("signature", "A. Okafor", nth=2, id="sig-text", kind="signature"),
]

# Tiny inline SVG stand-ins so the demo has a photo and a signature without files.
SAMPLE_PHOTO = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' width='280' height='180'>"
    "<rect fill='%23d7c4a8' width='280' height='180'/>"
    "<circle cx='140' cy='72' r='36' fill='%236b5344'/>"
    "<rect x='88' y='118' width='104' height='70' rx='52' fill='%234a372c'/>"
    "<text x='140' y='24' text-anchor='middle' font-size='11' "
    "font-family='sans-serif' fill='%23555'>STAFF PHOTO (invented)</text>"
    "</svg>"
)

SAMPLE_SIGNATURE = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' width='280' height='90'>"
    "<rect fill='%23fff' width='280' height='90'/>"
    "<path d='M20 55 C 60 20, 90 80, 140 40 S 220 20, 260 58' "
    "fill='none' stroke='%23111' stroke-width='3'/>"
    "<text x='20' y='80' font-size='11' font-family='cursive'>A. Okafor</text>"
    "</svg>"
)

SAMPLE_IMAGES = [
    {
        "id": "staff-photo",
        "alt": "Staff photo",
        "data_url": SAMPLE_PHOTO,
    },
    {
        "id": "wet-signature",
        "alt": "Signature",
        "data_url": SAMPLE_SIGNATURE,
    },
]

SAMPLE_SPANS += [
    {
        "id": "photo-1",
        "type": "personal_image",
        "start": 0,
        "end": 0,
        "kind": "personal_image",
        "image_id": "staff-photo",
        "bbox": [0.32, 0.18, 0.36, 0.55],
    },
    {
        "id": "sig-img",
        "type": "signature",
        "start": 0,
        "end": 0,
        "kind": "signature",
        "image_id": "wet-signature",
        "bbox": [0.05, 0.15, 0.9, 0.7],
    },
]
