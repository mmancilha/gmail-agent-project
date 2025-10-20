from sqlalchemy import Column, Integer, String, LargeBinary
from .database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email_gmail = Column(String, unique=True, index=True)
    
    # Encrypted fields
    client_id_encrypted = Column(LargeBinary, nullable=False)
    client_secret_encrypted = Column(LargeBinary, nullable=False)
    refresh_token_encrypted = Column(LargeBinary, nullable=False)

