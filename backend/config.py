"""Configuration constants for the document classifier."""
import re
from pathlib import Path

# ── Model Configuration ───────────────────────────────────────────────────────
MODEL = "gemma-4-31b-it"

# ── Filename Pattern ──────────────────────────────────────────────────────────
BILL_PATTERN = re.compile(r"^bill_", re.IGNORECASE)

# ── Valid Categories ──────────────────────────────────────────────────────────
VALID_CATEGORIES = {
    "Patient Bills",
    "Claim Forms",
    "KYC Documents",
    "Medical Reports",
    "Prescriptions",
    "Unknown",
}

# ── Classification Prompt ───────────────────────────────────────────────────
PROMPT = """Classify this document image into exactly one of these categories:
- Patient Bills
- Claim Forms
- KYC Documents
- Medical Reports
- Prescriptions

Reply with ONLY the category name, nothing else."""

# ── Keyword rules for OCR-based classification ────────────────────────────────
# Each entry: (category, [list of keyword patterns to search for])
# The first matching rule wins.
KEYWORD_RULES = [
    ("KYC Documents",  [r"government\s+of\s+india", r"govt\.?\s+of\s+india",
                        r"aadhaar", r"aadhar", r"income\s+tax\s+department",
                        r"passport\s+of\s+india"]),
    ("Claim Forms",    [r"claim\s+no", r"claim\s+number", r"claim\s+form",
                        r"medishield"]),
    ("Medical Reports",[r"test\s+name", r"lab\s+report", r"laboratory\s+report",
                        r"diagnostic\s+report", r"pathology", r"radiology",
                        r"haemoglobin", r"hemoglobin", r"blood\s+report"]),
    ("Prescriptions",  [r"\bprescription\b", r"\bdiagnosis\b", r"\brx\b",
                        r"sig\b", r"dosage", r"tablet", r"capsule",
                        r"prescribed\s+by"]),
    ("Patient Bills",  [r"invoice", r"bill\s+no", r"bill\s+to",
                        r"amount\s+due", r"total\s+amount", r"hospital\s+bill",
                        r"pharmacy"]),
]

# Compile all patterns once
COMPILED_RULES = [
    (category, [re.compile(pat, re.IGNORECASE) for pat in patterns])
    for category, patterns in KEYWORD_RULES
]
