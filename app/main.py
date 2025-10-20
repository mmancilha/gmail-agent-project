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
    # Add tags metadata for better organization in the docs
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
    # --- A CORREÇÃO ESTÁ AQUI ---
    status_code=status.HTTP_201_CREATED, # Era HTTP_21_CREATED
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
    Retrieves the most recent emails for a specific agent from their inbox.
    """
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    credentials_info = crud.get_decrypted_credentials(db_agent=db_agent)
    service = gmail_service.get_gmail_service(credentials_info)
    if service is None:
        raise HTTPException(status_code=500, detail="Could not connect to Gmail service. Check credentials.")
    
    emails = gmail_service.read_emails(service)
    return emails

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
    Reads an agent's latest emails, summarizes them using AI, 
    and forwards the summaries to a specified recipient.
    """
    print(f"--- Starting process for Agent ID: {agent_id} ---")

    # 1. Get the Agent and its credentials
    print("Step 1: Fetching agent from database...")
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        print(f"ERROR: Agent with ID {agent_id} not found.")
        raise HTTPException(status_code=404, detail="Agent not found")
    print("Agent found successfully.")
    
    print("Fetching and decrypting credentials...")
    credentials_info = crud.get_decrypted_credentials(db_agent=db_agent)
    gmail_service_instance = gmail_service.get_gmail_service(credentials_info)
    if gmail_service_instance is None:
        print("ERROR: Failed to connect to Gmail service.")
        raise HTTPException(status_code=500, detail="Could not connect to Gmail service. Check credentials.")
    print("Connection to Gmail established.")

    # 2. Read the latest emails
    print("Step 2: Reading emails...")
    emails = gmail_service.read_emails(gmail_service_instance, max_results=5) 
    if not emails:
        print("No new emails to process.")
        return {
            "status": "Success",
            "message": "No new emails to process.",
            "forwarded_to": request_body.recipient_email,
            "summaries_sent": 0
        }
    print(f"Found {len(emails)} emails to process.")

    # 3. Summarize and forward each email
    print("Step 3: Starting summary and forward loop...")
    summaries_sent_count = 0
    for i, email in enumerate(emails):
        print(f"  Processing email {i+1}/{len(emails)} from: {email['sender']}")
        
        # Generate summary with AI
        print("    Generating summary with AI...")
        summary = openai_service.summarize_text(email['content'])
        print("    Summary generated.")
        
        # Prepare the email to be forwarded
        forward_subject = f"Summary of: {email['subject']}"
        forward_body = (
            f"Hello,\n\n"
            f"Here is a summary of a recent email from {email['sender']}:\n\n"
            f"--- SUMMARY ---\n"
            f"{summary}\n\n"
            f"--- ORIGINAL CONTENT (Snippet) ---\n"
            f"{email['content'][:500]}..."
            f"\n\nBest regards,\nYour AI Agent"
        )

        # Send the email
        print(f"    Forwarding summary to: {request_body.recipient_email}")
        gmail_service.send_email(
            service=gmail_service_instance,
            to=request_body.recipient_email,
            subject=forward_subject,
            body=forward_body
        )
        print("    Email forwarded successfully.")
        summaries_sent_count += 1
    
    print(f"--- Process complete. {summaries_sent_count} summaries sent. ---")
    return {
        "status": "Success",
        "message": f"Processed and forwarded {summaries_sent_count} email summaries.",
        "forwarded_to": request_body.recipient_email,
        "summaries_sent": summaries_sent_count
    }

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Agent for Gmail API"}

