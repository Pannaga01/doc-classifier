# Multimodal AI Document Classifier

A document classification system that uses Regex, OCR and Large Language Models (LLM) to automatically categorize medical and administrative documents.

## Overview

This project classifies uploaded documents into the following categories:
- **Patient Bills** - Hospital invoices and billing statements
- **Claim Forms** - Insurance claim documents
- **KYC Documents** - Identity verification documents (Aadhaar, passport, etc.)
- **Medical Reports** - Lab reports, diagnostic reports, pathology results
- **Prescriptions** - Doctor prescriptions and medication orders

## Architecture

```
┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │
│  (Next.js)  │     │  (FastAPI)  │
└─────────────┘     └─────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
   ┌──────────┐    ┌──────────────┐  ┌──────────┐
   │ Filename │    │   OCR +      │  │   LLM    │
   │  Regex   │    │   Keywords   │  │ (Gemini) │
   └──────────┘    └──────────────┘  └──────────┘
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js, TypeScript, Axios |
| Backend | FastAPI, Python |
| OCR | EasyOCR |
| LLM | Google Gemini (gemma-4-31b-it) |
| Tracing | LangSmith |

## Features

- **Hybrid Classification Pipeline**: 
  1. First tries rule-based keyword matching using OCR
  2. Falls back to LLM classification if OCR cannot determine the category
- **Batch Processing**: Upload multiple documents at once
- **Drag & Drop Interface**: Easy-to-use web interface
- **Token Usage Tracking**: LangSmith integration for monitoring

## Project Structure

```
multimodal-ai/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── classify.py         # Classification logic
│   └── pyproject.toml      # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── page.tsx        # Main UI component
│   │   └── globals.css     # Global styles
│   ├── package.json        # Node.js dependencies
│   └── next.config.ts      # Next.js configuration
└── README.md               # This file
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google API Key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Create a `.env` file in the backend directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

5. Start the backend server:
   ```bash
   uvicorn app:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`

## API Endpoints

### POST /classify

Classify one or more document images.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `files` - List of image files (PNG, JPG)

**Response:**
```json
{
  "results": [
    {
      "file": "document1.png",
      "category": "Patient Bills"
    },
    {
      "file": "document2.png",
      "category": "Medical Reports"
    }
  ]
}
```

## Classification Logic

The classification uses a **multi-stage pipeline**:

1. **Filename Regex Check**:
   - Files starting with `bill_` are automatically classified as "Patient Bills"
   - Uses regex pattern: `^bill_` (case-insensitive)

2. **OCR + Keyword Matching**:
   - Extracts text from the image using EasyOCR
   - Searches the extracted text for category-specific keywords
   - Keywords are matched against patterns like "government of india", "aadhaar", "claim form", "lab report", "prescription", etc.
   - Returns the first matching category

3. **LLM Fallback**:
   - If OCR + keyword matching returns "Unknown", uses Google Gemini
   - Sends the image with a classification prompt to the model
   - Model returns the category name

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Google AI Studio API key for Gemini model |

## License

MIT License