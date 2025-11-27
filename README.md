# Medical-Appointment-Scheduling-Agent

A smart AI-powered medical appointment scheduling assistant that handles user queries, books appointments, and answers FAQs about clinic operations. Built with FastAPI, OpenAI LLMs, and Pinecone vector DB for memory management.

## Features
Handles natural language requests from patients
  - Schedules appointments via Calendly API
  - Maintains conversation memory for context-aware interactions
  - Summarizes responses for brevity
  - Provides clinic information: hours, services, address, and payment options
  - Confirms appointment details with the user before booking
  - Requires no medical or diagnostic advice

## Quick Start
Prerequisites: Python 3.10+, pip, and an OpenAI API key.

```bash
# Clone the repository
git clone https://github.com/yourusername/Medical-Appointment-Scheduling-Agent.git
cd Medical-Appointment-Scheduling-Agent
```
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
```bash
# Install all dependencies
pip install -r requirements.txt
```

## Setup an environment variable file with the following

```bash
openAIKey=YOUR_OPENAI_KEY_HERE
claudeKey=YOUR_CLAUDE_KEY_HERE
vectorDb=YOUR_PINECONE_API_KEY_HERE
dbIndex=YOUR_PINECONE_INDEX_NAME_HERE
embeddingModel=text-embedding-3-small
calendlyKey=YOUR_CALENDLY_API_KEY_HERE
dimension=1536
```

## Embed FAQ Data
Before running the app, you must generate embeddings from your FAQ data:
```bash
# Run the embedding script
python embed/embed.py

# Optional: test embeddings
python embed/testEmbed.py
```
This will create the necessary vectors in Pinecone for your FAQ tool to work.

## Run the FastAPI
```bash
uvicorn app:app --reload
```
You can now interact with the agent at:
```bash
http://127.0.0.1:8000
```

## Usage

Send a POST request to /chat with json Body:
```bash
{
    "message":"When does the clinic open and can I walk-in instead of an appointment"
}
```

## System Design – Medical Appointment Scheduling Agent
### Folder Structure Overview
```bash
Medical-Appointment-Scheduling-Agent/
│
├── app.py                   # Main FastAPI application
├── agentConfig.py           # Agent configuration & memory setup
├── tools/                   # Functional tools for the agent
│   ├── faqTool.py
│   ├── calendlyTools.py
├── utils.py                 # Utility functions for environment & variables
├── .env                     # Environment variables and secrets
├── embed/                   # Embedding related logic and data
│   ├── FAQ.json             # FAQ dataset for embeddings
│   ├── embed.py             # Functions to create embeddings
│   ├── testEmbed.py         # Test scripts for embeddings
└── README.md
```

# 



