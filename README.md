# AI Agent with Gmail API 🚀
FastAPI backend to register and operate AI agents that interact with the Gmail API. The service securely stores credentials, reads emails, summarizes content using AI, and can automatically reply based on intent and sentiment.

The goal is a simple, secure, production-ready API for tasks like reading received emails, summarization and forwarding, intelligent auto-reply, and agent management.

## 🧩 Project Structure
```text
gmail-agent-project
├── app/
│   ├── __init__.py
│   ├── crud.py
│   ├── database.py
│   ├── gmail_service.py
│   ├── main.py
│   ├── models.py
│   ├── openai_service.py
│   ├── schemas.py
│   └── security.py
├── README.md
└── requirements.txt
```

## ⚙️ Requirements
- Python 3.10+ (recommended)
- `pip` and `venv`
- Gmail OAuth 2.0 credentials (Client ID/Secret + Refresh Token)
- `OPENAI_API_KEY` (required for AI features)

## 🔧 Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/mmancilha/gmail-agent-project.git
   cd gmail-agent-project
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the `.env` file at project root:
   ```env
   # Database (SQLite by default)
   DATABASE_URL="sqlite:///./agents.db"

   # Generate a new key for encryption (Fernet)
   # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   FERNET_KEY="YOUR_FERNET_KEY"

   # OpenAI for summarization/replies
   OPENAI_API_KEY="your_openai_key"
   ```
5. Obtain a Gmail Refresh Token (OAuth):
   ```bash
   # Use the local flow to generate a token
   python app/get_refresh_token.py
   ```
   Copy the generated `refresh_token` — it will be used when registering the agent via API.
6. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000` (docs: `/docs`).

## 🧪 Basic Usage
Core endpoints (see `/docs` for details):

- Register agent
  ```bash
  curl -X POST http://127.0.0.1:8000/agents/ \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Sales AI Agent",
      "email_gmail": "your.email@gmail.com",
      "client_id": "<CLIENT_ID>",
      "client_secret": "<CLIENT_SECRET>",
      "refresh_token": "<REFRESH_TOKEN>"
    }'
  ```

- Read unread emails (primary inbox)
  ```bash
  curl http://127.0.0.1:8000/agents/<AGENT_ID>/emails/
  ```

- Auto-reply with sentiment analysis
  ```bash
  curl -X POST http://127.0.0.1:8000/agents/<AGENT_ID>/emails/auto-reply
  ```

- Summarize and forward
  ```bash
  curl -X POST http://127.0.0.1:8000/agents/<AGENT_ID>/emails/summarize-and-forward \
    -H "Content-Type: application/json" \
    -d '{"recipient_email": "manager@example.com"}'
  ```

Useful links:
- FastAPI Docs: https://fastapi.tiangolo.com
- Gmail API: https://developers.google.com/gmail/api
- OpenAI API: https://platform.openai.com/docs

## 🚀 Deployment
Application available on Render:

Live URL: **https://gmail-agent-project.onrender.com/docs**

> Note: On the free tier, the service may hibernate due to inactivity. If it takes time to start, wait ~30–60s and refresh the page.

---
Made with FastAPI, SQLAlchemy, OpenAI and Gmail API. ✨