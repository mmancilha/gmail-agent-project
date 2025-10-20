from pydantic import BaseModel, EmailStr, Field

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
        orm_mode = True
    
# --- Adicione as novas classes abaixo ---

# Schema para a resposta da leitura de e-mails
class EmailResponse(BaseModel):
    sender: str
    subject: str
    content: str

# Schema para o pedido de resumir e encaminhar
class SummarizeForwardRequest(BaseModel):
    recipient_email: EmailStr = Field(
        ...,
        description="The email address to forward the summaries to.",
        example="manager@example.com"
    )

# Schema para a resposta de sucesso
class SummarizeForwardResponse(BaseModel):
    status: str
    message: str
    forwarded_to: EmailStr
    summaries_sent: int

