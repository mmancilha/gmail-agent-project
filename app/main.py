from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import all necessary modules from our application
from . import crud, models, schemas, gmail_service, openai_service
from .database import SessionLocal, engine

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Agent with Gmail API",
    description="Backend to register and interact with AI agents on Gmail.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Agent Registration",
            "description": "Operations to register and manage AI agents.",
        },
        {
            "name": "Email Actions",
            "description": "Operations for reading and sending emails.",
        },
        {
            "name": "AI Actions",
            "description": "Endpoints that leverage AI to process emails.",
        },
    ]
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post(
    "/agents/",
    response_model=schemas.AgentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Agent Registration"]
)
def register_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    """
    Registers a new AI agent and securely stores its credentials.
    """
    db_agent = crud.get_agent_by_email(db, email=agent.email_gmail)
    if db_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud.create_agent(db=db, agent=agent)

@app.get(
    "/agents/{agent_id}/emails/",
    response_model=List[schemas.EmailResponse],
    tags=["Email Actions"]
)
def get_emails(agent_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the most recent unread emails for a specific agent from their primary inbox.
    """
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    credentials_info = crud.get_decrypted_credentials(db_agent=db_agent)
    service = gmail_service.get_gmail_service(credentials_info)
    if service is None:
        raise HTTPException(status_code=500, detail="Could not connect to Gmail service. Check credentials.")

    raw_emails = gmail_service.read_emails(service)
    return [{"sender": e["sender"], "subject": e["subject"], "content": e["content"]} for e in raw_emails]


@app.post(
    "/agents/{agent_id}/emails/summarize-and-forward",
    response_model=schemas.SummarizeForwardResponse,
    tags=["AI Actions"]
)
def summarize_and_forward_emails(
    agent_id: int,
    request_body: schemas.SummarizeForwardRequest,
    db: Session = Depends(get_db)
):
    """
    Reads an agent's latest unread emails, summarizes them using AI,
    and forwards the summaries to a specified recipient.
    """
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    credentials_info = crud.get_decrypted_credentials(db_agent=db_agent)
    gmail_service_instance = gmail_service.get_gmail_service(credentials_info)
    if gmail_service_instance is None:
        raise HTTPException(status_code=500, detail="Could not connect to Gmail service.")

    emails = gmail_service.read_emails(gmail_service_instance, max_results=5)
    if not emails:
        return {
            "status": "Success",
            "message": "No new unread emails to process.",
            "forwarded_to": request_body.recipient_email,
            "summaries_sent": 0
        }

    summaries_sent_count = 0
    for email in emails:
        summary = openai_service.summarize_text(email['content'])
        forward_subject = f"Summary of: {email['subject']}"
        forward_body = (
            f"Hello,\n\nHere is a summary of a recent email from {email['sender']}:\n\n"
            f"--- SUMMARY ---\n{summary}\n\n"
            f"--- ORIGINAL CONTENT (Snippet) ---\n{email['content'][:500]}...\n\n"
            f"Best regards,\nYour AI Agent"
        )
        gmail_service.send_email(
            service=gmail_service_instance,
            to=request_body.recipient_email,
            subject=forward_subject,
            body=forward_body
        )
        summaries_sent_count += 1

    return {
        "status": "Success",
        "message": f"Processed and forwarded {summaries_sent_count} email summaries.",
        "forwarded_to": request_body.recipient_email,
        "summaries_sent": summaries_sent_count
    }


@app.post(
    "/agents/{agent_id}/emails/auto-reply",
    response_model=schemas.AutoReplyResponse,
    tags=["AI Actions"]
)
def auto_reply_to_emails(agent_id: int, db: Session = Depends(get_db)):
    """
    Reads unread emails from the primary inbox, generates a reply using AI,
    and sends it to the original sender, ignoring promotional content.
    """
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    credentials_info = crud.get_decrypted_credentials(db_agent=db_agent)
    gmail_service_instance = gmail_service.get_gmail_service(credentials_info)
    if gmail_service_instance is None:
        raise HTTPException(status_code=500, detail="Could not connect to Gmail service.")

    unread_emails = gmail_service.read_emails(gmail_service_instance, max_results=5)
    if not unread_emails:
        return {
            "status": "Success",
            "message": "No new unread emails to reply to.",
            "replies_sent": 0
        }

    replies_sent_count = 0
    for email in unread_emails:
        reply_text = openai_service.generate_reply_text(
            original_sender=email["sender"],
            original_subject=email["subject"],
            original_content=email["content"]
        )

        if reply_text.strip().upper() == "IGNORE":
            print(f"AI decided to ignore promotional email from: {email['sender']}")
            continue

        gmail_service.send_reply(
            service=gmail_service_instance,
            original_message=email["full_message"],
            reply_body=reply_text
        )
        replies_sent_count += 1

    return {
        "status": "Success",
        "message": f"Processed {len(unread_emails)} emails and sent {replies_sent_count} replies.",
        "replies_sent": replies_sent_count
    }

# --- NEW ENDPOINT FOR 'Send Email' ---
@app.post(
    "/agents/{agent_id}/emails/send",
    response_model=schemas.SendEmailResponse,
    tags=["Email Actions"]
)
def send_one_click_email(
    agent_id: int,
    request_body: schemas.SendEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Sends a single, simple email from the agent's account.
    All inputs (recipient, subject, body) are provided by the user.
    """
    # 1. Get Agent and connect to Gmail
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    credentials_info = crud.get_decrypted_credentials(db_agent=db_agent)
    gmail_service_instance = gmail_service.get_gmail_service(credentials_info)
    if gmail_service_instance is None:
        raise HTTPException(status_code=500, detail="Could not connect to Gmail service.")

    # 2. Send the email using the provided inputs
    sent_message = gmail_service.send_email(
        service=gmail_service_instance,
        to=request_body.recipient_email,
        subject=request_body.subject,
        body=request_body.body
    )

    if sent_message is None:
        raise HTTPException(status_code=500, detail="Failed to send email.")

    return {
        "status": "success",
        "message": f"Email successfully sent with Message ID: {sent_message.get('id')}",
        "sent_to": request_body.recipient_email
    }

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Agent for Gmail API"}

