from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Agent with Gmail API",
    description="Backend to register and interact with AI agents on Gmail.",
    version="1.0.0"
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

    Args:
        agent (schemas.AgentCreate): The data for the agent to be created, including name,
                                     email, and Gmail credentials.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: Raised if the provided email is already registered in the system.

    Returns:
        schemas.AgentResponse: The newly created agent, excluding its sensitive credentials.
    """
    db_agent = crud.get_agent_by_email(db, email=agent.email_gmail)
    if db_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    return crud.create_agent(db=db, agent=agent)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the AI Agent for Gmail API"}