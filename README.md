# Margin — AI Resume Parser

Drop in a resume and get it back read, scored, and annotated — like a
mentor marked it up by hand. Built as an internship project at Pinnacle Labs.

![tech](https://img.shields.io/badge/backend-FastAPI-009688) ![tech](https://img.shields.io/badge/frontend-React-61DAFB) ![tech](https://img.shields.io/badge/AI-Groq-orange)

## What it does

- Accepts **PDF, DOCX, PNG, or JPG** resumes (with OCR fallback for scans/images)
- Extracts structured data: contact info, skills, education, experience
- Generates a **0–100 quality score** with constructive, specific feedback
- Suggests **2–4 realistic job roles** based on the candidate's background
- Renders it all as an "annotated paper" — hand-drawn score circle, sticky-note margin comments, handwritten typography

## Tech stack

| | |
|---|---|
| **Backend** | FastAPI, Groq API (`openai/gpt-oss-120b`), pdfplumber, python-docx, pytesseract |
| **Frontend** | React, Vite, plain CSS (no UI framework — custom design system) |

## Getting started

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add your GROQ_API_KEY from console.groq.com/keys
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

> Image/scanned-PDF uploads require `tesseract-ocr` and `poppler` installed
> locally (system packages, not Python packages). PDF and DOCX work without them.

## Security notes

- API key lives only in `backend/.env` (gitignored) — never exposed to the frontend
- Uploads are allow-listed by extension, size-capped, saved under randomized filenames, and deleted immediately after processing
- Rate-limited per IP, locked-down CORS, no internal errors leaked to the client

## License

MIT — feel free to fork and adapt.