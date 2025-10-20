from sqlalchemy.orm import Session
from . import models, schemas, security

def get_agent(db: Session, agent_id: int):
    """Fetches an agent by their primary key ID."""
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()

def get_agent_by_email(db: Session, email: str):
    """Fetches an agent by their email address."""
    return db.query(models.Agent).filter(models.Agent.email_gmail == email).first()

def get_decrypted_credentials(db_agent: models.Agent) -> dict:
    """
    Takes a database agent object and returns a dictionary with its
    decrypted credentials.
    """
    client_id = security.decrypt_data(db_agent.client_id_encrypted)
    client_secret = security.decrypt_data(db_agent.client_secret_encrypted)
    refresh_token = security.decrypt_data(db_agent.refresh_token_encrypted)
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/gmail.modify"]
    }

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

