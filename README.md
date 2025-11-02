# AI Agent with Gmail API

This project is a backend service built with FastAPI that registers AI agents to interact securely with the Gmail API. It manages encrypted credentials and exposes endpoints to read, send, and automate email workflows using AI.

## 🚀 Live Application

- Deployed API (Swagger UI): https://gmail-agent-project.onrender.com/docs
- Note: Hosted on Render free tier. If the page is slow to load, wait 30–60 seconds while the instance wakes up and refresh.

## ✨ Features

This API provides a complete set of endpoints for managing an AI agent’s interaction with Gmail:

1. Agent Management
   - `POST /agents/`: Register a new AI agent. Credentials (`client_id`, `client_secret`, `refresh_token`) are encrypted with Fernet before being stored.

2. Core Email Actions
   - `GET /agents/{agent_id}/emails/`: Fetch recent unread emails from the Primary Inbox (ignoring Promotions/Social).
   - `POST /agents/{agent_id}/emails/send`: Send a simple one‑click email by providing `to`, `subject`, and `body`.

3. AI‑Powered Actions
   - `POST /agents/{agent_id}/emails/summarize-and-forward`:
     - Read latest unread emails, summarize them with OpenAI (`gpt-4o-mini`), and forward summaries to a chosen recipient.
   - `POST /agents/{agent_id}/emails/auto-reply`:
     - Read latest unread emails and generate context‑aware replies with sentiment analysis.
     - Intelligent filtering of promotional/newsletter/automated messages.
     - Replies maintain the original thread with appropriate tone.

## 🧱 Project Structure

```text
/gmail_agent_project
├── /app
│   ├── __init__.py         
│   ├── crud.py             
│   ├── database.py         
│   ├── gmail_service.py    
│   ├── main.py             
│   ├── models.py           
│   ├── openai_service.py   
│   ├── schemas.py          
│   └── security.py         
├── .env                    
├── .gitignore              
├── requirements.txt        
├── get_refresh_token.py    
└── README.md               
```

## 🔧 Setup and Installation

### Prerequisites
- Python 3.8+
- Google Cloud project with Gmail API enabled
- OpenAI API key

### 1) Clone the repository
```bash
git clone https://github.com/mmancilha/gmail-agent-project.git
cd gmail-agent-project
```

### 2) Create and activate a virtual environment
```bash
# Create the environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Configure environment variables
Create a `.env` file in the project root and add:
```env
DATABASE_URL="sqlite:///./agents.db"

# Generate a key with:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FERNET_KEY="YOUR_NEWLY_GENERATED_FERNET_KEY_HERE"

OPENAI_API_KEY="sk-YOUR_OPENAI_API_KEY_HERE"
```

### 5) Generate Google credentials (refresh_token)
1. In Google Cloud Console, create OAuth 2.0 credentials for a “Desktop app”.
2. Download the JSON file and place it as `credentials.json` in the project root.
3. Run the helper script:
```bash
python app/get_refresh_token.py
```
4. Authorize in the browser. A `refresh_token` will be printed in the terminal to use when registering your agent.

## ▶️ Run Locally
With the virtual environment activated, from the project root, run:
```bash
uvicorn app.main:app --reload
```

- Local server: http://127.0.0.1:8000/

## 📚 API Documentation
- Swagger UI: http://127.0.0.1:8000/docs

---

Made with FastAPI, SQLAlchemy, OpenAI and Gmail API. ✨
