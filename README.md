# Headless Lead Qualifier Webhook (FastAPI)

A state-of-the-art FastAPI webhook listener engineered to sit between messy upstream lead sources (Meta Lead Ads, custom landing pages) and downstream CRM systems (GoHighLevel, Make.com, n8n). 

## Core Problem Solved
Marketing platforms frequently send malformed JSON payloads. When integrating via standard Make.com/Zapier webhooks, these malformed payloads silently fail with a `422 Unprocessable Entity` or `400 Bad Request` error, leading to lost leads and broken pipelines.

This architecture acts as an impenetrable shield:
1. **Strict Pydantic Validation:** Drops invalid payloads immediately or coerces data into safe schemas.
2. **LLM Normalization:** Uses an asynchronous OpenAI orchestration engine to analyze unstructured user inputs (e.g., "I want a cheap roof fix") and structure them into deterministic CRM tags.
3. **Zero-Fault Routing:** Guarantees that only structurally sound, highly-qualified leads ever hit the CRM pipeline.

## Installation (Plug & Play)

### 1. Requirements
- Python 3.10+
- FastAPI, Uvicorn, OpenAI

### 2. Setup
```bash
git clone https://github.com/Shiro291/ghl-make-qualifier.git
cd ghl-make-qualifier
pip install -r requirements.txt
```

### 3. Execution
Start the local Uvicorn server:
```bash
uvicorn index:app --reload --port 8000
```
Your webhook will now be listening on `http://localhost:8000/webhook`.

## Deployment
This architecture is built for serverless environments. It is configured to deploy directly to Vercel via zero-config. Simply push this repository to Vercel and it will expose the API endpoint globally.

*Engineered by Fathan Faqih Ali.*
