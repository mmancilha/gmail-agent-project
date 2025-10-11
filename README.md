# AI Agent with Gmail API
This project is a backend service developed with FastAPI that allows registering AI agents to interact with the Gmail API. The service handles secure storage of credentials and provides endpoints for managing emails.

## Project Structure
/gmail_agent_project
```text
/gmail_agent_project
├── /app
│   ├── __init__.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── security.py
├── .env
├── requirements.txt
└── README.md
```

## Features (Deliverable 1)
- Agent Registration: Securely register new AI agents via a POST request.

- Credential Encryption: All sensitive credentials (client_id, client_secret, refresh_token) are encrypted before being stored in the database.

- Automatic API Documentation: Interactive API documentation available at /docs.

## Prerequisites
- Python 3.8+

- A virtual environment tool (like venv)

## Setup and Installation
### Clone the repository:
```bash
git clone https://github.com/mmancilha/gmail-agent-project.git
cd gmail-agent-project
```

### Create and activate a virtual environment:
```bash
# Create the environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### Install the dependencies:
```bash
pip install -r requirements.txt
```

### Configure environment variables:
Create a file named .env in the project root by copying the example below.

```env
# .env
DATABASE_URL="sqlite:///./agents.db"

# To generate a new key, run in your terminal:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FERNET_KEY="YOUR_NEWLY_GENERATED_KEY_HERE"
```

## How to Run the Application
With the virtual environment activated, run the following command from the root directory (gmail_agent_project):

```bash
uvicorn app.main:app --reload
```

The application will be available at http://127.0.0.1:8000.

## API Documentation
Once the server is running, you can access the interactive API documentation (Swagger UI) at:

http://127.0.0.1:8000/docs

## Deployment
This application is deployed on Render.

Live URL: https://gmail-agent-project.onrender.com/docs

> Note: This application is hosted on Render's free tier. The service may "spin down" due to inactivity. If the link does not load immediately, please wait 30-60 seconds for the server to restart and then refresh the page.