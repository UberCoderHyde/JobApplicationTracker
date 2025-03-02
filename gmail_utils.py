# gmail_utils.py
import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_authenticate(creds_path='credentials/gmail_credentials.json', token_path='credentials/gmail_token.pickle'):
    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_unread_emails(service):
    results = service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
    messages = results.get('messages', [])
    email_data_list = []
    if not messages:
        print("No new unread emails found.")
        return email_data_list
    for msg in messages:
        msg_id = msg['id']
        msg_details = service.users().messages().get(userId='me', id=msg_id).execute()
        headers = msg_details['payload']['headers']
        subject = ''
        from_email = ''
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                from_email = header['value']
        body_text = ''
        payload = msg_details['payload']
        parts = payload.get('parts', [])
        if not parts:
            body_data = payload.get('body', {}).get('data')
            if body_data:
                body_text = base64.urlsafe_b64decode(body_data).decode('utf-8')
        else:
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        email_data_list.append({
            'id': msg_id,
            'subject': subject,
            'from': from_email,
            'body': body_text
        })
    return email_data_list

def mark_email_as_read(service, msg_id):
    service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
