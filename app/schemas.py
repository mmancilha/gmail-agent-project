from pydantic import BaseModel, EmailStr, Field
from typing import List

# Schema for receiving data when creating an agent
class AgentCreate(BaseModel):
    name: str = Field(
        ..., 
        description="The agent's name for easy identification.",
        example="Sales AI Agent"
    )
    email_gmail: EmailStr = Field(
        ...,
        description="The Gmail address the agent will manage.",
        example="your.email@gmail.com"
    )
    client_id: str = Field(
        ...,
        description="The Client ID obtained from Google Cloud Console for OAuth 2.0.",
        example="1234567890-abcde.apps.googleusercontent.com"
    )
    client_secret: str = Field(
        ...,
        description="The Client Secret obtained from Google Cloud Console.",
        example="GOCSPX-ABCDE12345"
    )
    refresh_token: str = Field(
        ...,
        description="The Refresh Token obtained through the OAuth 2.0 consent flow.",
        example="1//AbCdEfGhIjKlMnOpQrStUvWxYz"
    )

# Schema for returning data (without exposing secrets)
class AgentResponse(BaseModel):
    id: int
    name: str
    email_gmail: EmailStr

    class Config:
        from_attributes = True # Updated from 'orm_mode' for Pydantic v2

# Schema for the response of reading emails
class EmailResponse(BaseModel):
    sender: str
    subject: str
    content: str

# Schema for the summarize and forward request
class SummarizeForwardRequest(BaseModel):
    recipient_email: EmailStr = Field(
        ...,
        description="The email address to forward the summaries to.",
        example="manager@example.com"
    )

# Schema for the summarize and forward response
class SummarizeForwardResponse(BaseModel):
    status: str
    message: str
    forwarded_to: EmailStr
    summaries_sent: int

# Schema for the auto-reply response
class AutoReplyResponse(BaseModel):
    status: str
    message: str
    replies_sent: int

# --- NEW SCHEMAS FOR 'Send Email' ---

class SendEmailRequest(BaseModel):
    recipient_email: EmailStr = Field(
        ..., 
        description="The recipient's email address."
    )
    subject: str = Field(
        ..., 
        min_length=1, 
        description="The subject line of the email."
    )
    body: str = Field(
        ..., 
        min_length=1, 
        description="The plain text content of the email."
    )

class SendEmailResponse(BaseModel):
    status: str = "success"
    message: str
    sent_to: EmailStr

