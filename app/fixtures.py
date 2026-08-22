"""Synthetic demo documents for Privacy Gate.

SYNTHETIC ONLY — never a real person's payslip or bank statement (see
.claude/skills/privacy-gate/SKILL.md, "Seed demos with synthetic documents").

Extends the design.md §3.2 fixtures with an email, phone, and date of birth
so tests have real fixture text to exercise all 9 FieldType values against
(ADR-011). The planted net-pay-vs-deposit inconsistency (£2,427.40 vs
£2,480.00) is kept because docs and the reasoner tests reference it.

Note: the payslip deliberately shows only one "Account"-labelled number
("Account: 4417") so the context-aware account_number regex (D-11) has a
single, unambiguous match to test against.
"""

from __future__ import annotations

PAYSLIP = """\
PAYSLIP: July 2026
Employee: A. Okafor
Date of Birth: 03 May 1994
Email: a.okafor@example.co.uk
Phone: 07700 900123
NI Number: QQ123456C
Address: 14 Pelham St, SW7 2AZ
Account: 4417
Sort Code: 12-34-56

Gross Pay: £2,840.00
Tax Deducted: £412.60
Net Pay: £2,427.40

Employer: Pelham Consulting Ltd
Pay Date: 25 July 2026
"""

BANK_STATEMENT = """\
BANK STATEMENT: Account 12345678
Account Holder: A. Okafor
Email: a.okafor@example.co.uk
Sort Code: 12-34-56
Statement Period: 01 Jul 2026 - 31 Jul 2026

Date       Description              Amount
25 Jul 26  PELHAM CONSULTING PAY    £2,480.00
28 Jul 26  RENT PELHAM ST           -£1,200.00
30 Jul 26  SAINSBURY'S              -£84.32

Balance: £1,195.68
"""

DOCUMENTS = {"payslip": PAYSLIP, "bank_statement": BANK_STATEMENT}
