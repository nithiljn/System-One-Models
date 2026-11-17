# AI Job Resume Fitment Matcher

AI Job Resume Fitment Matcher is a fast candidate evaluation tool. It compares a candidate resume against a target job description using Google Gemini models.

The system uses a two speed architecture. It delivers initial screening decisions in approximately 200 milliseconds with zero output token costs. It also provides detailed resume audits on demand.

## Architecture

1. System 1 Fast Decision Engine
The primary screening pass uses the Google Gemini Decision 1 model. It evaluates candidate fitment directly against structured criteria without generating free text. This results in zero output tokens and very fast response times.

2. System 2 Deep Resume Audit
When a detailed breakdown is needed, the system calls Gemini Flash Lite. It identifies missing technical skills, highlights resume red flags, and provides actionable recommendations.

## Core Features

1. Zero Output Token Cost
The model answers closed set questions directly through log probabilities. This eliminates output token charges during initial screening.

2. Sub 200 Millisecond Latency
Screening decisions are completed quickly, making it suitable for high volume candidate review.

3. In Memory PDF Resume Extraction
Users can upload resumes in PDF format. Text is extracted in memory without storing files on disk. Users can remove uploaded files and clear the input at any time.

4. Objective Match Scoring
The application rates candidate fitment on a 0 to 10 rubric score, checks mandatory criteria, and detects critical dealbreakers.

5. High Contrast Interface
The interface uses an ivory and dark theme designed for clear document reading and easy review.

## Tech Stack

* Backend: Python 3.12, FastAPI, Uvicorn
* AI Models: Google Gemini Decision 1, Google Gemini Flash Lite
* SDK: Google GenAI SDK
* Document Processing: PyPDF
* Frontend: HTML5, Tailwind CSS, Vanilla JavaScript
* Deployment: Vercel Serverless ASGI

## Local Installation

1. Create and activate a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install required packages

```bash
pip install -r requirements.txt
```

3. Set your Google Gemini API key

Create a file named `.env` in this directory:

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

4. Start the local server

```bash
uvicorn main.py:app --host 0.0.0.0 --port 7860 --reload
```

Open your browser and navigate to `http://localhost:7860`.

## License

This project is licensed under the MIT License.
