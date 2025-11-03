import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

scopes = ['https://www.googleapis.com/auth/gmail.modify']
cred_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
token_path = os.path.join(os.path.dirname(__file__), 'token.pickle')

def get_gmail_service():
    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(cred_path, scopes)
        creds = flow.run_local_server(port=8080)
        with open(token_path, 'wb') as f:
            pickle.dump(creds, f)

    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_unread_snippets(max_results=5):
    svc = get_gmail_service()
    res = svc.users().messages().list(userId='me', q='is:unread', maxResults=max_results).execute()
    items = res.get('messages', [])
    emails = []
    for m in items:
        msg = svc.users().messages().get(userId='me', id=m['id'], format='full').execute()
        headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
        snippet = msg.get('snippet', '')
        emails.append({
            'id': m['id'],
            'from': headers.get('From'),
            'subject': headers.get('Subject'),
            'snippet': snippet
        })
        svc.users().messages().modify(userId='me', id=m['id'], body={'removeLabelIds': ['UNREAD']}).execute()
    return emails