# Real Mail MCP Server

This is a FastMCP server for managing Gmail emails. It provides tools for sending, reading (inbox/sent), searching, forwarding, replying, and basic categorization of emails using SMTP for outgoing and IMAP for incoming. The server supports rich HTML email formatting for sending complex, styled emails.

## Setup

1. **Prerequisites**:
   - Python 3.11+
   - Install dependencies: `pip install fastmcp python-dotenv`

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

2. **get_emails(folder: str = 'inbox', limit: int = 10, start: int = 0, unread_only: bool = False)**  
   Fetches emails from specified folder (e.g., 'inbox' or '[Gmail]/Sent Mail'). Returns dicts with id, subject, from/to, date, body preview.

3. **get_unread_count(folder: str = 'inbox')**  
   Returns count of unread emails in folder.

4. **delete_email(email_id: str, folder: str = 'inbox')**  
   Permanently deletes an email by ID from folder (use with caution).

5. **search_emails(keywords: list, date_from: str = None, date_to: str = None, sender: str = None, folder: str = 'inbox')**  
   Searches email bodies for keywords, with optional date range (DD-MMM-YYYY), sender filter, and folder (top 10).

6. **forward_email(email_id: str, to: str, custom_subject: str = None, custom_body_prefix: str = None, is_html: bool = False, folder: str = 'inbox')**  
   Forwards an email with optional custom prefix/subject from folder.

7. **reply_to_email(email_id: str, reply_body: str, is_html: bool = False, subject_prefix: str = "Re:", folder: str = 'inbox')**  
   Sends a reply to an email from folder.

8. **create_label(label_name: str)**  
   Placeholder for creating Gmail labels (requires Gmail API for full support).

9. **delete_label(label_name: str)**  
   Placeholder for deleting labels.

10. **add_label_to_email(email_id: str, label_name: str, folder: str = 'inbox')**  
    Limited: Sets IMAP flag (not true Gmail label; API needed for full).

## Testing

- Run `python test_functions.py` for basic tool tests (sending, fetching, searching, etc.).
- Run `python test_html_email.py` for HTML email test.
- Run `python test_forward_reply.py` for forwarding/replying and enhanced search tests.
- Run `python test_sent_emails.py` for fetching sent emails.
- Tests send to self and skip destructive actions like delete for safety.

## Limitations

- Label management is placeholder/limited (IMAP doesn't fully support Gmail labels; integrate Gmail API for production).
- HTML rendering varies by email client; use inline styles for best compatibility.
- No authentication beyond basic login; add OAuth for security.
- Searches are body-only with basic filters; extend further if needed.
- Forwarding includes original as text; for rich forward, API may be better.
- Folder names are Gmail-specific; adjust for other providers.

## TODO

Future improvements:
- Integrate Gmail API for full label support (create, delete, apply).
- Add OAuth2 authentication instead of app passwords.
- Support fetching attachments from emails.
- Implement email rules/filters creation via API.
- Enhance search with more advanced queries (attachments, labels).
- Add support for multiple email accounts.
- Include unit tests with mocking.
- Add logging and error metrics.
- Support embedded images in HTML emails (CID attachments) fully.
- Bulk operations (forward multiple, delete multiple).

For agent integration, see [prompt.txt](prompt.txt) for usage instructions and examples.

## License

MIT License (or as per your preference).
