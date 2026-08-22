window.PRIVACY_EXPORT_DEMO = {
  "documentName": "payslip",
  "text": "ACME LTD  —  PAYSLIP\nPeriod: July 2026\n\nEmployee: A. Okafor\nNI number: QQ123456C\nAddress: 14 Pelham St, SW7\nEmail: a.okafor@example.com\nPhone: 07700 900123\nAccount: 4417\nDate of birth: 14 Mar 1998\n\nGross pay: £2,840.00\nTax paid: £412.60\nNet pay: £2,427.40\n\nSignature: A. Okafor\n",
  "spans": [
    {
      "id": "name-1",
      "type": "name",
      "start": 50,
      "end": 59,
      "value": "A. Okafor",
      "kind": "text"
    },
    {
      "id": "ni_number",
      "type": "ni_number",
      "start": 71,
      "end": 80,
      "value": "QQ123456C",
      "kind": "text"
    },
    {
      "id": "address",
      "type": "address",
      "start": 90,
      "end": 107,
      "value": "14 Pelham St, SW7",
      "kind": "text"
    },
    {
      "id": "email",
      "type": "email",
      "start": 115,
      "end": 135,
      "value": "a.okafor@example.com",
      "kind": "text"
    },
    {
      "id": "phone",
      "type": "phone",
      "start": 143,
      "end": 155,
      "value": "07700 900123",
      "kind": "text"
    },
    {
      "id": "account_number",
      "type": "account_number",
      "start": 165,
      "end": 169,
      "value": "4417",
      "kind": "text"
    },
    {
      "id": "date_of_birth",
      "type": "date_of_birth",
      "start": 185,
      "end": 196,
      "value": "14 Mar 1998",
      "kind": "text"
    },
    {
      "id": "sig-text",
      "type": "signature",
      "start": 268,
      "end": 277,
      "value": "A. Okafor",
      "kind": "signature"
    },
    {
      "id": "photo-1",
      "type": "personal_image",
      "start": 0,
      "end": 0,
      "kind": "personal_image",
      "image_id": "staff-photo",
      "bbox": [
        0.32,
        0.18,
        0.36,
        0.55
      ]
    },
    {
      "id": "sig-img",
      "type": "signature",
      "start": 0,
      "end": 0,
      "kind": "signature",
      "image_id": "wet-signature",
      "bbox": [
        0.05,
        0.15,
        0.9,
        0.7
      ]
    }
  ],
  "images": [
    {
      "id": "staff-photo",
      "alt": "Staff photo",
      "data_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='280' height='180'><rect fill='%23d7c4a8' width='280' height='180'/><circle cx='140' cy='72' r='36' fill='%236b5344'/><rect x='88' y='118' width='104' height='70' rx='52' fill='%234a372c'/><text x='140' y='24' text-anchor='middle' font-size='11' font-family='sans-serif' fill='%23555'>STAFF PHOTO (invented)</text></svg>"
    },
    {
      "id": "wet-signature",
      "alt": "Signature",
      "data_url": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='280' height='90'><rect fill='%23fff' width='280' height='90'/><path d='M20 55 C 60 20, 90 80, 140 40 S 220 20, 260 58' fill='none' stroke='%23111' stroke-width='3'/><text x='20' y='80' font-size='11' font-family='cursive'>A. Okafor</text></svg>"
    }
  ]
};
