# Roo's Notes for Real Mail MCP

- Credentials are loaded from .env (SMTP_USER, SMTP_PASS, etc.).
- IMAP uses Gmail's server; ensure app password is used for SMTP_PASS.
- Labels (create/delete/add) have limited functionality without Gmail API integration.
- For production, add error handling and security.
- Tested: Sending HTML emails with formatting works; reading/searching/unread count work; forwarding/replying tested; deletion untested for safety; labels are placeholders.
- See README.md for full setup, limitations, and TODOs.

These notes are for my reference during development and maintenance.