import base64
from email.mime.text import MIMEText
from email import message_from_bytes
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ALTERAÇÃO IMPORTANTE: Mudamos a permissão para permitir envio de e-mails.
# 'gmail.modify' permite ler, enviar e modificar e-mails.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service(credentials_info: dict):
    """Cria e retorna um objeto de serviço da API do Gmail."""
    try:
        creds = Credentials.from_authorized_user_info(credentials_info, SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Ocorreu um erro ao construir o serviço: {e}")
        return None

# NOVA FUNÇÃO: Adicionamos esta função para enviar e-mails.
def send_email(service, to: str, subject: str, body: str):
    """
    Envia um e-mail usando a API do Gmail.

    Args:
        service: O objeto de serviço autenticado da API do Gmail.
        to (str): O endereço de e-mail do destinatário.
        subject (str): O assunto do e-mail.
        body (str): O conteúdo em texto do e-mail.

    Returns:
        dict: O objeto da mensagem enviada pela API, ou None se falhar.
    """
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # A API requer que a mensagem seja codificada em base64url
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        
        sent_message = service.users().messages().send(
            userId="me", 
            body=create_message
        ).execute()
        
        print(f"ID da Mensagem: {sent_message['id']}")
        return sent_message
    except HttpError as error:
        print(f'Ocorreu um erro ao enviar o e-mail: {error}')
        return None

def read_emails(service, max_results=5):
    """Recupera os e-mails mais recentes da caixa de entrada."""
    try:
        # O código desta função permanece o mesmo de antes.
        results = service.users().messages().list(
            userId='me', 
            labelIds=['INBOX'],
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        email_list = []
        if not messages:
            return []
            
        for message_info in messages:
            msg = service.users().messages().get(
                userId='me', id=message_info['id'], format='raw'
            ).execute()
            
            raw_email_data = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
            email_message = message_from_bytes(raw_email_data)
            
            sender = email_message['From']
            subject = email_message['Subject']
            
            content = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == 'text/plain':
                        content = part.get_payload(decode=True).decode('utf-8', 'ignore')
                        break
            else:
                if email_message.get_content_type() == 'text/plain':
                    content = email_message.get_payload(decode=True).decode('utf-8', 'ignore')

            email_list.append({
                "sender": sender,
                "subject": subject,
                "content": content.strip()
            })
            
        return email_list

    except HttpError as error:
        print(f'Ocorreu um erro ao ler os e-mails: {error}')
        return []

