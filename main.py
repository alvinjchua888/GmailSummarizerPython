"""
Gmail Summarizer - Main Script
This script fetches emails from Gmail and generates summaries using AI.
"""

import os
from gmail_client import GmailClient
from summarizer import EmailSummarizer
from config import Config


def main():
    """Main function to run the Gmail Summarizer."""
    print("=" * 50)
    print("Gmail Summarizer")
    print("=" * 50)
    
    # Initialize configuration
    config = Config()
    
    # Initialize Gmail client
    print("\n[1/3] Connecting to Gmail...")
    gmail_client = GmailClient(config.CREDENTIALS_FILE, config.TOKEN_FILE)
    
    # Initialize summarizer
    print("[2/3] Initializing AI summarizer...")
    summarizer = EmailSummarizer(config.API_KEY)
    
    # Fetch emails
    print(f"[3/3] Fetching last {config.MAX_EMAILS} emails...")
    emails = gmail_client.fetch_recent_emails(max_results=config.MAX_EMAILS)
    
    if not emails:
        print("\nNo emails found.")
        return
    
    print(f"\nFound {len(emails)} emails. Generating summaries...\n")
    print("=" * 50)
    
    # Summarize each email
    for i, email in enumerate(emails, 1):
        print(f"\n[Email {i}/{len(emails)}]")
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        print(f"Date: {email['date']}")
        print("-" * 50)
        
        # Generate summary
        summary = summarizer.summarize(email['body'])
        print(f"Summary:\n{summary}")
        print("=" * 50)
    
    print("\n✓ Summarization complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
