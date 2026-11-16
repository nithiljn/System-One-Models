---
title: System One Job Resume Fitment Matcher
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.32.0
app_file: app.py
pinned: false
---

# System One // Job-Resume Fitment Matcher

A high-speed candidate fitment evaluation platform powered by **Google Gemini Decision-1** (System-1) and **Gemini 3.5 Flash Lite** (System-2 Deep Audit).

## Features
* **Zero Output Token Latency:** Evaluates candidate eligibility, match tier, and 10-level rubric score in ~200ms using Google's closed-set Decisions API.
* **In-Memory PDF Resume Upload:** Upload `.pdf` resumes directly with instantaneous text extraction via `pypdf`.
* **On-Demand Deep Audit:** System-2 critique identifying missing technical skills, resume red flags, and concrete recommendations.
* **Deep Sea Blue Theme:** Clean, high-contrast dark aesthetic with zero emojis and responsive viewport scaling.
* **Dockerized Production Deployment:** Runs seamlessly on Hugging Face Spaces with 16GB RAM.

## Local Development

```bash
# 1. Install dependencies
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Add your GEMINI_API_KEY to .env
echo "GEMINI_API_KEY=your_key_here" > .env

# 3. Launch server
python main.py
```

Open `http://localhost:7860` in your browser.
