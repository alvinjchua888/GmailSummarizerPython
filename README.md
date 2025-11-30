# Gmail Summarizer

A Python application that fetches emails from Gmail and generates AI-powered summaries using OpenAI's GPT models.

## Features

- 📧 Fetch recent emails from Gmail using Gmail API
- 🤖 Generate concise summaries using OpenAI GPT
- 🔐 Secure OAuth2 authentication with Gmail
- ⚙️ Configurable email filters and summary settings
- 🎯 Easy-to-use command-line interface

## Prerequisites

- Python 3.7 or higher
- Gmail account
- OpenAI API key
- Google Cloud Project with Gmail API enabled

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Gmail-Summarizer-Python
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials and save as `credentials.json` in the project root

### 4. Set up OpenAI API

1. Get your API key from [OpenAI](https://platform.openai.com/api-keys)
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

## Usage

Run the application:

```bash
python main.py
```

On first run, you'll be prompted to authorize the application to access your Gmail account. After authorization, the app will:

1. Connect to Gmail
2. Fetch the specified number of recent emails (default: 10)
3. Generate AI summaries for each email
4. Display the summaries in the terminal

## Configuration

Edit the `.env` file to customize settings:

- `MAX_EMAILS`: Number of emails to fetch (default: 10)
- `EMAIL_QUERY`: Gmail search query (e.g., `is:unread`, `from:example@email.com`)
- `SUMMARY_MAX_LENGTH`: Maximum summary length in words (default: 150)
- `AI_MODEL`: OpenAI model to use (default: gpt-3.5-turbo)

## Project Structure

```
Gmail-Summarizer-Python/
├── main.py              # Main application script
├── gmail_client.py      # Gmail API client
├── summarizer.py        # Email summarizer using OpenAI
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Security Notes

- Never commit `credentials.json`, `token.pickle`, or `.env` files to version control
- Keep your API keys secure
- The `.gitignore` file is configured to exclude sensitive files

## Troubleshooting

### "Credentials file not found"
Make sure you've downloaded the OAuth credentials from Google Cloud Console and saved them as `credentials.json` in the project root.

### "OPENAI_API_KEY not found"
Ensure you've created a `.env` file (not `.env.example`) and added your OpenAI API key.

### "No emails found"
Check your email query in the `.env` file. An empty query fetches all emails, but specific queries might not match any emails.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
