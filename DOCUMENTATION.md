# Gmail Summarizer - Technical Documentation

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Code Flow](#code-flow)
- [Module Details](#module-details)
- [API Integration](#api-integration)
- [Authentication Flow](#authentication-flow)
- [Data Flow](#data-flow)
- [Error Handling](#error-handling)
- [Configuration Management](#configuration-management)

---

## Overview

The Gmail Summarizer is a Python application that automates the process of fetching emails from Gmail and generating concise summaries using OpenAI's GPT models. The application uses OAuth2 for secure Gmail authentication and the OpenAI API for intelligent text summarization.

### Key Technologies
- **Gmail API**: For fetching and reading emails
- **OpenAI API**: For generating AI-powered summaries
- **OAuth2**: For secure authentication
- **Python 3.7+**: Core programming language

---

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
┌─────────────┐
│   main.py   │  ← Entry point & orchestration
└──────┬──────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  config.py  │  │gmail_client │  │ summarizer  │
│             │  │    .py      │  │    .py      │
└─────────────┘  └──────┬──────┘  └──────┬──────┘
                        │                 │
                        ▼                 ▼
                 ┌─────────────┐  ┌─────────────┐
                 │  Gmail API  │  │ OpenAI API  │
                 └─────────────┘  └─────────────┘
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `main.py` | Application entry point, orchestrates workflow |
| `config.py` | Manages configuration and environment variables |
| `gmail_client.py` | Handles Gmail API authentication and email fetching |
| `summarizer.py` | Generates AI summaries using OpenAI |

---

## Code Flow

### High-Level Execution Flow

```
1. Application Start (main.py)
   ↓
2. Load Configuration (.env file)
   ↓
3. Authenticate with Gmail (OAuth2)
   ↓
4. Fetch Recent Emails (Gmail API)
   ↓
5. For Each Email:
   ├─ Extract email metadata (from, subject, date)
   ├─ Extract email body (text/plain or text/html)
   ├─ Send to OpenAI for summarization
   └─ Display summary
   ↓
6. Complete & Exit
```

### Detailed Step-by-Step Process

1. **Initialization Phase**
   ```python
   config = Config()  # Loads .env variables
   gmail_client = GmailClient(credentials_file, token_file)
   summarizer = EmailSummarizer(api_key)
   ```

2. **Gmail Authentication**
   - Checks for existing `token.pickle` file
   - If token exists and is valid → use it
   - If token expired → refresh it
   - If no token → initiate OAuth2 flow (opens browser)
   - Save token for future use

3. **Email Fetching**
   - Query Gmail API for message IDs
   - Fetch full message details for each ID
   - Parse headers (From, Subject, Date)
   - Extract body (handles both plain text and HTML)

4. **Summarization**
   - Send email body to OpenAI API
   - Use GPT model to generate concise summary
   - Return formatted summary

5. **Display Results**
   - Print email metadata
   - Print AI-generated summary
   - Continue to next email

---

## Module Details

### 1. main.py - Application Entry Point

**Purpose**: Orchestrates the entire workflow and handles user interaction.

**Key Functions**:

```python
def main():
    """
    Main execution function that:
    1. Initializes configuration
    2. Sets up Gmail client
    3. Sets up AI summarizer
    4. Fetches and summarizes emails
    5. Displays results
    """
```

**Error Handling**:
- `KeyboardInterrupt`: Graceful shutdown on Ctrl+C
- `Exception`: Catches and displays any runtime errors

**Flow Control**:
- Sequential processing of emails
- Early exit if no emails found
- Progress indicators for user feedback

---

### 2. config.py - Configuration Management

**Purpose**: Centralizes all configuration settings and environment variables.

**Configuration Variables**:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OPENAI_API_KEY` | string | required | OpenAI API authentication key |
| `GMAIL_CREDENTIALS_FILE` | string | `credentials.json` | Path to Gmail OAuth credentials |
| `GMAIL_TOKEN_FILE` | string | `token.pickle` | Path to saved authentication token |
| `MAX_EMAILS` | int | `10` | Number of emails to fetch |
| `EMAIL_QUERY` | string | `''` | Gmail search query filter |
| `SUMMARY_MAX_LENGTH` | int | `150` | Maximum summary length in words |
| `AI_MODEL` | string | `gpt-3.5-turbo` | OpenAI model to use |

**Key Methods**:

```python
@classmethod
def validate(cls):
    """
    Validates required configuration is present.
    Raises ValueError if OPENAI_API_KEY is missing.
    Warns if credentials file not found.
    """
```

**Environment Loading**:
- Uses `python-dotenv` to load `.env` file
- Falls back to default values if variables not set
- Type conversion for numeric values

---

### 3. gmail_client.py - Gmail API Integration

**Purpose**: Handles all interactions with the Gmail API.

**Class: GmailClient**

#### Initialization
```python
def __init__(self, credentials_file='credentials.json', token_file='token.pickle'):
    """
    Initializes Gmail client and authenticates.
    
    Args:
        credentials_file: OAuth2 credentials from Google Cloud Console
        token_file: Cached authentication token
    """
```

#### Key Methods

##### `_authenticate()`
**Purpose**: Handles OAuth2 authentication with Gmail.

**Process**:
1. Check for existing token in `token.pickle`
2. Validate token (check expiration)
3. If expired: refresh using refresh token
4. If no token: initiate OAuth2 flow
   - Opens browser for user authorization
   - User grants permissions
   - Receives authorization code
   - Exchanges code for access token
5. Save token to `token.pickle` for reuse

**Returns**: Authenticated Gmail API service object

**Scopes Used**:
- `https://www.googleapis.com/auth/gmail.readonly` (read-only access)

---

##### `fetch_recent_emails(max_results=10, query='')`
**Purpose**: Fetches recent emails from Gmail.

**Parameters**:
- `max_results`: Number of emails to fetch
- `query`: Gmail search query (e.g., `is:unread`, `from:boss@company.com`)

**Process**:
1. Call Gmail API `users().messages().list()`
2. Receive list of message IDs
3. For each message ID:
   - Call `_get_email_details(message_id)`
   - Parse and structure email data
4. Return list of email dictionaries

**Returns**: List of email objects with structure:
```python
{
    'id': 'message_id',
    'subject': 'Email Subject',
    'from': 'sender@example.com',
    'date': 'Mon, 1 Jan 2024 12:00:00',
    'body': 'Email content...'
}
```

---

##### `_get_email_details(message_id)`
**Purpose**: Fetches complete details for a specific email.

**Process**:
1. Call Gmail API `users().messages().get()` with format='full'
2. Extract headers using `_get_header()`
   - Subject
   - From
   - Date
3. Extract body using `_get_email_body()`
4. Return structured email object

**Error Handling**: Returns `None` if fetch fails

---

##### `_get_email_body(payload)`
**Purpose**: Extracts email body from Gmail message payload.

**Handles Multiple Formats**:
- **Multipart emails**: Emails with multiple MIME parts
  - Prefers `text/plain` parts
  - Falls back to `text/html` if plain text unavailable
  - Strips HTML tags from HTML content
- **Simple emails**: Single-part messages
  - Direct body extraction

**Base64 Decoding**: 
- Gmail returns body in base64url encoding
- Decodes using `base64.urlsafe_b64decode()`

**HTML Stripping**:
- Uses regex to remove HTML tags
- Decodes HTML entities (`&nbsp;`, `&amp;`, etc.)

---

##### `_strip_html(html)`
**Purpose**: Removes HTML tags and decodes entities.

**Process**:
1. Remove all HTML tags using regex: `<.*?>`
2. Decode common HTML entities
3. Return clean text

**Example**:
```python
Input:  "<p>Hello &amp; welcome!</p>"
Output: "Hello & welcome!"
```

---

### 4. summarizer.py - AI Summarization

**Purpose**: Generates concise email summaries using OpenAI GPT.

**Class: EmailSummarizer**

#### Initialization
```python
def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
    """
    Initializes the summarizer with OpenAI credentials.
    
    Args:
        api_key: OpenAI API key
        model: GPT model to use (gpt-3.5-turbo or gpt-4)
    """
```

#### Key Methods

##### `summarize(email_body: str, max_length: int = 150)`
**Purpose**: Generates a summary of an email.

**Process**:
1. **Input Validation**
   - Check if email body is not empty
   - Return "No content to summarize" if empty

2. **Content Truncation**
   - Limit to 4000 characters to avoid token limits
   - Prevents API errors from excessive input

3. **Prompt Creation**
   - Generates structured prompt using `_create_prompt()`
   - Instructs AI on summary requirements

4. **API Call**
   ```python
   openai.ChatCompletion.create(
       model=self.model,
       messages=[
           {"role": "system", "content": "System instructions..."},
           {"role": "user", "content": "Email to summarize..."}
       ],
       max_tokens=300,
       temperature=0.5
   )
   ```

5. **Extract & Return Summary**
   - Parse API response
   - Extract summary text
   - Return formatted summary

**Parameters**:
- `email_body`: The email content to summarize
- `max_length`: Target summary length in words

**Returns**: String containing the summary

**Error Handling**: Returns error message if API call fails

---

##### `_create_prompt(email_body: str, max_length: int)`
**Purpose**: Creates an optimized prompt for the AI model.

**Prompt Structure**:
```
Instructions:
- Summarize in approximately {max_length} words
- Focus on key points
- Identify action items
- Highlight important information

Email content:
{email_body}

Summary:
```

**Optimization Techniques**:
- Clear, specific instructions
- Word limit guidance
- Focus areas defined
- Structured format

---

##### `batch_summarize(emails: list)`
**Purpose**: Summarizes multiple emails efficiently.

**Process**:
1. Iterate through email list
2. Call `summarize()` for each email
3. Collect summaries with metadata
4. Return list of summary objects

**Returns**: List of dictionaries:
```python
[
    {
        'email_id': 'id',
        'subject': 'Subject',
        'summary': 'Generated summary...'
    },
    ...
]
```

**Use Case**: Batch processing for better performance tracking

---

## API Integration

### Gmail API Integration

**Authentication Method**: OAuth 2.0

**API Endpoints Used**:

1. **List Messages**
   ```
   GET https://gmail.googleapis.com/gmail/v1/users/me/messages
   ```
   - Fetches list of message IDs
   - Supports query parameters for filtering

2. **Get Message**
   ```
   GET https://gmail.googleapis.com/gmail/v1/users/me/messages/{id}
   ```
   - Fetches full message details
   - Returns headers, body, and metadata

**Rate Limits**: 
- 1 billion quota units per day
- List operation: 5 units
- Get operation: 5 units
- Typical usage: 10 emails = ~50 units

---

### OpenAI API Integration

**Authentication Method**: API Key (Bearer token)

**API Endpoint Used**:
```
POST https://api.openai.com/v1/chat/completions
```

**Request Structure**:
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant..."
    },
    {
      "role": "user",
      "content": "Please summarize..."
    }
  ],
  "max_tokens": 300,
  "temperature": 0.5
}
```

**Parameters Explained**:
- `model`: GPT model version
- `messages`: Chat-based conversation format
- `max_tokens`: Maximum length of response (not input)
- `temperature`: Creativity level (0.0-2.0, lower = more focused)

**Token Limits**:
- GPT-3.5-turbo: 4,096 tokens (input + output)
- Input: ~3,000 characters = ~750 tokens
- Output: 300 tokens max

**Cost** (approximate):
- GPT-3.5-turbo: $0.002 per 1K tokens
- 10 emails with summaries: ~$0.02

---

## Authentication Flow

### Gmail OAuth2 Flow

```
┌──────────┐
│   User   │
│  Starts  │
│   App    │
└────┬─────┘
     │
     ▼
┌────────────────┐      Yes      ┌─────────────┐
│ Token exists?  ├─────────────→ │ Load Token  │
└────┬───────────┘               └──────┬──────┘
     │ No                               │
     │                                  ▼
     │                          ┌───────────────┐     Yes
     │                          │ Token Valid?  ├────────→ [Use Token]
     │                          └───────┬───────┘
     │                                  │ No
     │                                  ▼
     │                          ┌───────────────┐     Yes
     │                          │ Has Refresh?  ├────────→ [Refresh Token]
     │                          └───────┬───────┘
     │                                  │ No
     │                                  │
     └──────────────┬───────────────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ Open Browser    │
           │ for OAuth       │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ User Authorizes │
           │ in Browser      │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ Receive Auth    │
           │ Code            │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ Exchange for    │
           │ Access Token    │
           └────────┬────────┘
                    │
                    ▼
           ┌─────────────────┐
           │ Save Token      │
           │ to token.pickle │
           └────────┬────────┘
                    │
                    ▼
              [Use Token]
```

**Security Features**:
- Tokens stored locally in `token.pickle`
- Refresh tokens allow seamless re-authentication
- No password storage required
- Read-only scope limits access

---

## Data Flow

### Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     START APPLICATION                     │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Load .env    │
                    │  Configuration│
                    └───────┬───────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│                    GMAIL API SECTION                       │
│                                                            │
│  ┌─────────────┐         ┌──────────────┐                │
│  │ Authenticate│────────→│ Get Token    │                │
│  │ with OAuth2 │         │ (cached)     │                │
│  └─────┬───────┘         └──────────────┘                │
│        │                                                   │
│        ▼                                                   │
│  ┌─────────────┐         ┌──────────────┐                │
│  │ Request     │────────→│ Receive      │                │
│  │ Message IDs │         │ ID List      │                │
│  └─────┬───────┘         └──────┬───────┘                │
│        │                        │                         │
│        │                        ▼                         │
│        │                 ┌──────────────┐                │
│        │                 │ For Each ID  │                │
│        │                 └──────┬───────┘                │
│        │                        │                         │
│        ▼                        ▼                         │
│  ┌─────────────────────────────────────┐                │
│  │ Fetch Full Message Details          │                │
│  │  - Headers (From, Subject, Date)    │                │
│  │  - Body (Plain text or HTML)        │                │
│  │  - Base64 decode content            │                │
│  └────────────────┬────────────────────┘                │
└───────────────────┼──────────────────────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │ Email Data    │
            │ Structure     │
            │ {id, from,    │
            │  subject,     │
            │  date, body}  │
            └───────┬───────┘
                    │
                    ▼
┌───────────────────────────────────────────────────────────┐
│                   OPENAI API SECTION                       │
│                                                            │
│  ┌─────────────┐         ┌──────────────┐                │
│  │ Format      │────────→│ Create       │                │
│  │ Email Body  │         │ AI Prompt    │                │
│  └─────┬───────┘         └──────┬───────┘                │
│        │                        │                         │
│        │                        ▼                         │
│        │                 ┌──────────────┐                │
│        │                 │ Send to      │                │
│        │                 │ OpenAI API   │                │
│        │                 └──────┬───────┘                │
│        │                        │                         │
│        │                        ▼                         │
│        │                 ┌──────────────┐                │
│        │                 │ GPT Model    │                │
│        │                 │ Processes    │                │
│        │                 └──────┬───────┘                │
│        │                        │                         │
│        │                        ▼                         │
│        │                 ┌──────────────┐                │
│        │                 │ Receive      │                │
│        │                 │ Summary      │                │
│        │                 └──────┬───────┘                │
└────────┼────────────────────────┼───────────────────────┘
         │                        │
         └────────────┬───────────┘
                      │
                      ▼
              ┌───────────────┐
              │ Display to    │
              │ User:         │
              │  - From       │
              │  - Subject    │
              │  - Date       │
              │  - Summary    │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ More Emails?  ├──Yes──→ [Loop Back]
              └───────┬───────┘
                      │ No
                      ▼
              ┌───────────────┐
              │     END       │
              └───────────────┘
```

---

## Error Handling

### Error Handling Strategy

The application implements multiple layers of error handling:

#### 1. **Main Application Level** (main.py)

```python
try:
    main()
except KeyboardInterrupt:
    # User pressed Ctrl+C - graceful shutdown
    print("\n\nProcess interrupted by user.")
except Exception as e:
    # Catch-all for unexpected errors
    print(f"\n✗ Error: {str(e)}")
```

**Handles**:
- User interruption (Ctrl+C)
- All uncaught exceptions
- Provides user-friendly error messages

---

#### 2. **Configuration Level** (config.py)

```python
if not cls.API_KEY:
    raise ValueError("OPENAI_API_KEY not found")

if not os.path.exists(cls.CREDENTIALS_FILE):
    print(f"Warning: Gmail credentials file not found")
```

**Handles**:
- Missing required configuration
- Missing credential files
- Invalid environment variables

---

#### 3. **Gmail Client Level** (gmail_client.py)

**Authentication Errors**:
```python
if not os.path.exists(self.credentials_file):
    raise FileNotFoundError(
        f"Credentials file '{self.credentials_file}' not found"
    )
```

**API Errors**:
```python
try:
    results = self.service.users().messages().list(...)
except HttpError as error:
    print(f'An error occurred: {error}')
    return []
```

**Handles**:
- Missing credentials files
- API quota exceeded
- Network connectivity issues
- Invalid message IDs
- Malformed email data

---

#### 4. **Summarizer Level** (summarizer.py)

```python
try:
    response = openai.ChatCompletion.create(...)
    summary = response.choices[0].message.content.strip()
    return summary
except Exception as e:
    return f"Error generating summary: {str(e)}"
```

**Handles**:
- API authentication failures
- Rate limiting
- Token limit exceeded
- Network timeouts
- Invalid API responses

---

### Common Error Scenarios

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError: credentials.json` | Gmail OAuth credentials missing | Download from Google Cloud Console |
| `ValueError: OPENAI_API_KEY not found` | API key not in .env file | Add key to .env file |
| `HttpError: 401 Unauthorized` | Invalid API credentials | Check credentials validity |
| `HttpError: 429 Too Many Requests` | API rate limit exceeded | Wait and retry, implement backoff |
| `Token limit exceeded` | Email too long | Already handled by truncation |
| `Connection timeout` | Network issues | Check internet connection |

---

## Configuration Management

### Environment Variables

**Location**: `.env` file (not committed to git)

**Loading Process**:
1. `python-dotenv` loads `.env` on import
2. `os.getenv()` retrieves variables with defaults
3. Type conversion for numeric values
4. Validation of required variables

### Configuration Hierarchy

```
1. Environment Variables (.env file)
   ↓ (if not found)
2. Default Values (hardcoded in config.py)
   ↓ (if invalid)
3. Validation Error (raises exception)
```

### Security Best Practices

**Never Commit**:
- `.env` file (actual secrets)
- `credentials.json` (OAuth credentials)
- `token.pickle` (authentication tokens)

**Safe to Commit**:
- `.env.example` (template without secrets)
- `.gitignore` (excludes sensitive files)
- All code files

### Configuration Validation

The `Config` class can validate configuration:

```python
Config.validate()  # Checks for required variables
```

**Validation Checks**:
- ✓ `OPENAI_API_KEY` must be present
- ✓ `credentials.json` should exist (warning only)
- ✓ Numeric values are convertible to int

---

## Performance Considerations

### Token Usage Optimization

**Gmail API**:
- Batching not implemented (sequential requests)
- Each email = 2 API calls (list + get)
- 10 emails = ~50 quota units (well under daily limit)

**OpenAI API**:
- Email truncated to 4000 chars to save tokens
- Temperature 0.5 balances quality and speed
- Max tokens 300 limits response length

### Processing Time

**Approximate Times**:
- Gmail authentication: 0-2 seconds (cached) or 10-30 seconds (first time)
- Fetch 10 emails: 5-10 seconds
- Summarize 1 email: 2-5 seconds
- **Total for 10 emails**: ~30-60 seconds

### Optimization Opportunities

1. **Parallel Processing**: Summarize emails concurrently
2. **Caching**: Store summaries to avoid re-processing
3. **Batch API Calls**: Use Gmail batch API endpoint
4. **Streaming**: Stream OpenAI responses for faster UX

---

## Extending the Application

### Potential Enhancements

1. **Database Storage**
   - Store emails and summaries in SQLite/PostgreSQL
   - Track which emails have been processed

2. **Web Interface**
   - Flask/FastAPI web server
   - React/Vue.js frontend
   - Real-time summarization

3. **Scheduling**
   - Cron job for periodic summarization
   - Email digest notifications

4. **Advanced Filtering**
   - Filter by sender, date range, labels
   - Priority detection
   - Action item extraction

5. **Export Options**
   - PDF reports
   - CSV exports
   - Integration with note-taking apps

6. **Multiple Models**
   - Support for Claude, Gemini, etc.
   - Model comparison mode
   - Fallback model selection

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "Credentials file not found"
**Solution**: Download OAuth credentials from Google Cloud Console
1. Go to console.cloud.google.com
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download as `credentials.json`

#### Issue: "OPENAI_API_KEY not found"
**Solution**: Create `.env` file with API key
```bash
cp .env.example .env
# Edit .env and add your API key
```

#### Issue: "No emails found"
**Solution**: Check `EMAIL_QUERY` in `.env`
- Empty query fetches all emails
- Invalid query might match nothing
- Try `EMAIL_QUERY=is:inbox` to fetch inbox emails

#### Issue: "Rate limit exceeded"
**Solution**: Wait or reduce `MAX_EMAILS`
- Gmail: 1 billion quota units/day (unlikely to hit)
- OpenAI: Depends on tier (implement backoff)

---

## Conclusion

This documentation provides a comprehensive understanding of how the Gmail Summarizer works, from high-level architecture to detailed implementation specifics. The modular design ensures maintainability, while the error handling and configuration management provide robustness and flexibility.

For questions or contributions, please refer to the main README.md file.

---

**Last Updated**: November 30, 2025
**Version**: 1.0.0
