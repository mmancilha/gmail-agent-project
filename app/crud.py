from sqlalchemy.orm import Session
from . import models, schemas, security

def get_agent_by_email(db: Session, email: str):
    """Fetches an agent by their email address."""
    return db.query(models.Agent).filter(models.Agent.email_gmail == email).first()

def create_agent(db: Session, agent: schemas.AgentCreate):
    """Creates a new agent in the database with encrypted credentials."""
    
    # Encrypt credentials before saving
    encrypted_client_id = security.encrypt_data(agent.client_id)
    encrypted_client_secret = security.encrypt_data(agent.client_secret)
    encrypted_refresh_token = security.encrypt_data(agent.refresh_token)

    # Create the new Agent object for the database
    db_agent = models.Agent(
        name=agent.name,
        email_gmail=agent.email_gmail,
        client_id_encrypted=encrypted_client_id,
        client_secret_encrypted=encrypted_client_secret,
        refresh_token_encrypted=encrypted_refresh_token
    )

    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    return db_agent

