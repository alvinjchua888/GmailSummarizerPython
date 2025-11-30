"""
Email Summarizer Module
Generates summaries of email content using AI.
"""

from openai import OpenAI
from typing import Optional


class EmailSummarizer:
    """Summarizes email content using OpenAI GPT."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize the email summarizer.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for summarization (default: gpt-3.5-turbo)
        """
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
    
    def summarize(self, email_body: str, max_length: int = 150) -> str:
        """
        Summarize an email body.
        
        Args:
            email_body: The email content to summarize
            max_length: Maximum length of summary in words
        
        Returns:
            Summary of the email
        """
        if not email_body or len(email_body.strip()) == 0:
            return "No content to summarize."
        
        # Truncate very long emails to avoid token limits
        if len(email_body) > 4000:
            email_body = email_body[:4000] + "..."
        
        try:
            prompt = self._create_prompt(email_body, max_length)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes emails concisely and accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.5
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
        
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def _create_prompt(self, email_body: str, max_length: int) -> str:
        """
        Create a prompt for the AI model.
        
        Args:
            email_body: The email content
            max_length: Maximum length of summary
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""Please summarize the following email in approximately {max_length} words or less. 
Focus on the key points, action items, and important information.

Email content:
{email_body}

Summary:"""
        return prompt
    
    def batch_summarize(self, emails: list) -> list:
        """
        Summarize multiple emails.
        
        Args:
            emails: List of email dictionaries with 'body' key
        
        Returns:
            List of summaries
        """
        summaries = []
        for email in emails:
            summary = self.summarize(email.get('body', ''))
            summaries.append({
                'email_id': email.get('id'),
                'subject': email.get('subject'),
                'summary': summary
            })
        return summaries
