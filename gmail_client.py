"""
Gmail Client Module
Handles authentication and email fetching from Gmail API.
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from datetime import datetime
import re


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailClient:
    """Client for interacting with Gmail API."""
    
    def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
        """
        Initialize Gmail client with credentials.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to save/load authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API and return service object."""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials are invalid or don't exist, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)
    
    def fetch_recent_emails(self, max_results=10, query=''):
        """
        Fetch recent emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to fetch
            query: Gmail search query (e.g., 'is:unread', 'from:example@email.com')
        
        Returns:
            List of email dictionaries with keys: id, from, subject, date, body
        """
        try:
            # Fetch message IDs
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            # Fetch full message details
            emails = []
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
        
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def _get_email_details(self, message_id):
        """
        Get detailed information for a specific email.
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            Dictionary with email details
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            # Extract headers
            subject = self._get_header(headers, 'Subject')
            from_email = self._get_header(headers, 'From')
            date = self._get_header(headers, 'Date')
            
            # Extract body
            body = self._get_email_body(message['payload'])
            
            return {
                'id': message_id,
                'subject': subject,
                'from': from_email,
                'date': date,
                'body': body
            }
        
        except HttpError as error:
            print(f'Error fetching email {message_id}: {error}')
            return None
    
    def _get_header(self, headers, name):
        """Extract a specific header value from email headers."""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _get_email_body(self, payload):
        """
        Extract email body from payload.
        
        Args:
            payload: Email payload from Gmail API
        
        Returns:
            Email body as string
        """
        body = ''
        
        if 'parts' in payload:
            # Multipart email
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        html_body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        body = self._strip_html(html_body)
        else:
            # Simple email
            if 'data' in payload['body']:
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8')
        
        return body.strip()
    
    def _strip_html(self, html):
        """Remove HTML tags from text."""
        # Remove HTML tags
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', html)
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        return text.strip()
