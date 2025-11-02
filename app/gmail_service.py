import base64
from email.mime.text import MIMEText
from email import message_from_bytes, header
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any

# SCOPES for read and modify permissions
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service(credentials_info: dict) -> Any:
    """Creates and returns a Gmail API service object."""
    try:
        creds = Credentials.from_authorized_user_info(credentials_info, SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"An error occurred while building the service: {e}")
        return None

def send_email(service: Any, to: str, subject: str, body: str) -> Dict:
    """
    Sends a new email using the Gmail API.
    """
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}
        
        sent_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f"Message Id: {sent_message['id']}")
        return sent_message
    except HttpError as error:
        print(f'An error occurred while sending the email: {error}')
        return None

def send_reply(service: Any, original_message: Dict, reply_body: str) -> Dict:
    """
    Sends a reply to an existing email thread.
    """
    try:
        original_headers = {h['name'].lower(): h['value'] for h in original_message['payload']['headers']}
        
        message = MIMEText(reply_body)
        message['to'] = original_headers.get('reply-to') or original_headers.get('from')
        message['from'] = original_headers.get('to')
        message['subject'] = f"Re: {original_headers.get('subject', '')}"
        
        message['In-Reply-To'] = original_headers.get('message-id')
        message['References'] = original_headers.get('references') or original_headers.get('message-id')

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {
            'raw': encoded_message,
            'threadId': original_message['threadId']
        }
        
        sent_message = service.users().messages().send(userId="me", body=create_message).execute()
        print(f"Reply Sent. Message Id: {sent_message['id']}")
        return sent_message
    except HttpError as error:
        print(f'An error occurred while sending the reply: {error}')
        return None
    except Exception as e:
        print(f"An unexpected error occurred in send_reply: {e}")
        return None

def read_emails(service: Any, max_results: int = 5) -> List[Dict]:
    """
    Retrieves the most recent unread emails from the PRIMARY inbox.
    """
    try:
        # --- UPDATED QUERY ---
        # We now specify `category:primary` to ignore Promotions, Social, etc.
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            q="is:unread category:primary", # Only from the primary inbox
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        email_list = []
        if not messages:
            return []
            
        for message_info in messages:
            msg = service.users().messages().get(
                userId='me', id=message_info['id'], format='full'
            ).execute()
            
            headers = {h['name'].lower(): h['value'] for h in msg['payload']['headers']}
            sender = headers.get('from', 'Unknown Sender')
            subject = headers.get('subject', 'No Subject')
            
            content = ""
            if msg['payload'].get('parts'):
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        encoded_content = part['body'].get('data', '')
                        content = base64.urlsafe_b64decode(encoded_content).decode('utf-8', 'ignore')
                        break
            else:
                encoded_content = msg['payload']['body'].get('data', '')
                if encoded_content:
                    content = base64.urlsafe_b64decode(encoded_content).decode('utf-8', 'ignore')

            email_list.append({
                "full_message": msg,
                "sender": sender,
                "subject": subject,
                "content": content.strip()
            })
            
        return email_list

    except HttpError as error:
        print(f'An error occurred while reading emails: {error}')
        return []

