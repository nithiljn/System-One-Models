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

## Project Directory

```text
System-One-Models/
├── README.md
├── vercel.json
└── job-fitment-matcher/
    ├── main.py
    ├── config.py
    ├── models.py
    ├── requirements.txt
    ├── test_api.py
    ├── vercel.json
    ├── services/
    │   ├── __init__.py
    │   └── decision_service.py
    └── static/
        ├── index.html
        ├── style.css
        ├── app.js
        ├── favicon.svg
        └── gemini-decision-1.svg
```

## Local Installation

1. Clone the repository

```bash
git clone https://github.com/nithiljn/System-One-Models.git
cd System-One-Models/job-fitment-matcher
```

2. Create and activate a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install required packages

```bash
pip install -r requirements.txt
```

4. Set your Google Gemini API key

Create a file named `.env` in the `job-fitment-matcher` directory:

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

5. Start the local server

```bash
uvicorn main.py:app --host 0.0.0.0 --port 7860 --reload
```

Open your browser and navigate to `http://localhost:7860`.

## API Endpoints

1. Health Check
* Method: GET
* Path: `/health`
* Description: Returns server readiness and active model names.

2. Evaluate Fitment (System 1)
* Method: POST
* Path: `/api/evaluate-fitment`
* Payload: `{"job_description": "...", "resume_content": "..."}`
* Description: Executes fast evaluation with zero output tokens.

3. Deep Resume Audit (System 2)
* Method: POST
* Path: `/api/deep-audit`
* Payload: `{"job_description": "...", "resume_content": "..."}`
* Description: Returns missing technical skills, red flags, and recommendations.

4. Extract PDF Content
* Method: POST
* Path: `/api/extract-pdf`
* Payload: Multipart form file upload (.pdf)
* Description: Extracts text from an uploaded resume in memory.

## License

This project is licensed under the MIT License.
