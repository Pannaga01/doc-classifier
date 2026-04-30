import os
import csv
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
import easyocr
from fastapi import FastAPI, HTTPException,UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from langsmith import traceable,get_current_run_tree
from typing import List
import tempfile
import time

from config import (
    MODEL,
    BILL_PATTERN,
    VALID_CATEGORIES,
    PROMPT,
    COMPILED_RULES,
)

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI(title="Document classifier", version="0.1")
# -------------------------------
# CORS Middleware
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all origins
    allow_credentials=True,
    allow_methods=["*"],        # allow all HTTP methods
    allow_headers=["*"],        # allow all headers
)

# ── OCR reader (initialise once, English only) ────────────────────────────────
ocr_reader = easyocr.Reader(["en"], gpu=False)

@traceable(name="OCR Classification")
def classify_via_ocr(image_path: Path) -> str:
    """Extract text with EasyOCR and match against keyword rules."""
    start = time.time()
    results = ocr_reader.readtext(str(image_path), detail=0)
    text = " ".join(results)

    for category, patterns in COMPILED_RULES:
        if any(pat.search(text) for pat in patterns):
            duration = time.time() - start

            run = get_current_run_tree()
            if run:
                run.metadata.update({
                    "stage": "ocr",
                    "time_taken": duration,
                    "cost": 0
                })
            return category

    return "Unknown"

@traceable(name="LLM Classification")
def classify_via_llm(image_path: Path) -> str:
    start = time.time()
    response = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=image_path.read_bytes(), mime_type="image/png"),
            types.Part.from_text(text=PROMPT),
        ],
    )
    duration = time.time() - start
    usage = getattr(response, "usage_metadata", None)

    input_tokens = getattr(usage, "prompt_token_count", None) if usage else None
    output_tokens = getattr(usage, "candidates_token_count", None) if usage else None

    total_tokens = (
        input_tokens + output_tokens
        if input_tokens and output_tokens else None
    )

    run = get_current_run_tree()
    if run:
        run.metadata.update({
            "stage": "llm",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "time_taken": duration
        })
    category = response.text.strip().strip('"').strip("'")
    return category if category in VALID_CATEGORIES else "Unknown"

@traceable(name="Filename Pattern Classification")
def classify_via_filename(filename: str) -> str:
    """Check if filename matches the bill pattern."""
    if BILL_PATTERN.match(filename):
        return "Patient Bills"
    return "Unknown"

@traceable(name="Document Classification Pipeline")
def classify_document(file_path: Path, filename:str) -> str:
    # Classification pipeline
    category = classify_via_filename(filename)
    if category == "Unknown":
        category = classify_via_ocr(file_path)
        if category == "Unknown":
            category = classify_via_llm(file_path)
    return category

@app.post("/classify")
async def main(files: List[UploadFile] = File(...)):
    print("Received:", [f.filename for f in files])
    results = []

    for file in files:
        try:
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = Path(tmp.name)

            category = classify_document(tmp_path, file.filename)
            results.append({
                "file": file.filename,
                "category": category
            })

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"results": results}