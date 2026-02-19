# Real Mail MCP Server

This is a FastMCP server for managing Gmail emails. It provides tools for sending, reading, searching, and basic categorization of emails using SMTP for outgoing and IMAP for incoming. The server supports rich HTML email formatting for sending complex, styled emails.

## Setup

1. **Prerequisites**:
   - Python 3.11+
   - Install dependencies: `pip install fastmcp python-dotenv imaplib2` (imaplib is standard, but ensure smtplib and email are available).

2. **Configuration**:
   - Create a `.env` file with your Gmail credentials:
     ```
     SMTP_HOST=smtp.gmail.com
     SMTP_PORT=465
     SMTP_USER=your-email@gmail.com
     SMTP_PASS=your-app-password  # Use Gmail App Password, not regular password
     SMTP_FROM=your-email@gmail.com
     ```
   - For Gmail, enable 2FA and generate an App Password for SMTP/IMAP access.

3. **Running the Server**:
   - `fastmcp run server.py`
   - This starts the MCP server with stdio transport for integration with AI agents.

## Available Tools

The server exposes these tools via FastMCP:

1. **send_email(to: str, subject: str, body: str, is_html: bool = False, attachments: list = None)**  
   Sends an email. Supports HTML for formatting (colors, sizes, bold, lists, links, tables).  
   - Example HTML body: See [prompt.txt](prompt.txt) for details.

2. **get_emails(limit: int = 10, start: int = 0, unread_only: bool = False)**  
   Fetches emails from inbox (returns dicts with id, subject, from, date, body preview).

3. **get_unread_count()**  
   Returns count of unread emails.

4. **delete_email(email_id: str)**  
   Permanently deletes an email by ID (use with caution).

5. **search_emails(keywords: list)**  
   Searches email bodies for keywords (returns top 10 matches with id, subject, from).

6. **create_label(label_name: str)**  
   Placeholder for creating Gmail labels (requires Gmail API for full support).

7. **delete_label(label_name: str)**  
   Placeholder for deleting labels.

8. **add_label_to_email(email_id: str, label_name: str)**  
   Limited: Sets IMAP flag (not true Gmail label; API needed for full).

## Testing

- Run `python test_functions.py` for basic tool tests (sending, fetching, searching, etc.).
- Run `python test_html_email.py` for HTML email test.
- Tests send to self and skip destructive actions like delete for safety.

## Limitations

- Label management is placeholder/limited (IMAP doesn't fully support Gmail labels; integrate Gmail API for production).
- HTML rendering varies by email client; use inline styles for best compatibility.
- No authentication beyond basic login; add OAuth for security.
- Searches are body-only; extend to subject/sender if needed.

## TODO

Future improvements:
- Integrate Gmail API for full label support (create, delete, apply).
- Add OAuth2 authentication instead of app passwords.
- Support fetching attachments from emails.
- Implement email forwarding or replying tools.
- Add filtering rules creation via API.
- Enhance search with date ranges, sender filters.
- Add support for multiple email accounts.
- Include unit tests with mocking.
- Add logging and error metrics.
- Support embedded images in HTML emails (CID attachments).

For agent integration, see [prompt.txt](prompt.txt) for usage instructions and examples.

## License

MIT License (or as per your preference).