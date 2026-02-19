import asyncio
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import imaplib
import email as email_parser
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
SMTP_FROM = os.getenv('SMTP_FROM')

IMAP_HOST = 'imap.gmail.com'
IMAP_PORT = 993

mcp = FastMCP("email-server")

@mcp.tool
async def send_email(to: str, subject: str, body: str, is_html: bool = False, attachments: list = None):
    """
    Send an email using SMTP. Supports HTML formatting for complex layouts, colors, fonts, etc.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text or full HTML if is_html=True)
        is_html: If True, treat body as HTML (supports <h1>, <p style="color:red; font-size:24px;">, etc.)
        attachments: List of file paths to attach
    """
    msg = MIMEMultipart('alternative' if is_html else 'mixed')
    msg['From'] = SMTP_FROM
    msg['To'] = to
    msg['Subject'] = subject
    
    if is_html:
        # Plain text fallback (simple extraction from HTML or placeholder)
        plain_body = body.replace('<', '').replace('>', ' ').strip()[:500] + '...' if len(body) > 500 else body.replace('<', '').replace('>', ' ').strip()
        plain_msg = MIMEText(plain_body, 'plain')
        html_msg = MIMEText(body, 'html')
        msg.attach(plain_msg)
        msg.attach(html_msg)
    else:
        msg.attach(MIMEText(body, 'plain'))
    
    if attachments:
        for file_path in attachments:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}',
            )
            msg.attach(part)
    
    try:
        smtp_server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        smtp_server.login(SMTP_USER, SMTP_PASS)
        text = msg.as_string()
        smtp_server.sendmail(SMTP_FROM, to, text)
        smtp_server.quit()
        return "Email sent successfully"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

@mcp.tool
async def get_emails(limit: int = 10, start: int = 0, unread_only: bool = False):
    """
    Retrieve emails from inbox.
    
    Args:
        limit: Number of emails to retrieve
        start: Starting index (0-based)
        unread_only: If True, only unread emails
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select('inbox')
        
        search_term = 'ALL' if not unread_only else 'UNSEEN'
        status, messages = mail.search(None, search_term)
        if status != 'OK':
            raise Exception(f"Search failed: {status}")
        email_ids_bytes = messages[0].split()
        email_ids = [eid.decode('utf-8', errors='replace') for eid in email_ids_bytes]
        email_ids = email_ids[start:start + limit]
        
        emails = []
        for email_id in email_ids:
            try:
                status, msg_data = mail.fetch(email_id.encode('utf-8'), '(RFC822)')
                if status != 'OK':
                    continue
                raw_email = msg_data[0][1]
                email_message = email_parser.message_from_bytes(raw_email)
                
                subject = email_message['Subject'] or 'No Subject'
                from_email = email_message['From'] or 'Unknown'
                date = email_message['Date'] or 'Unknown'
                
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                            except:
                                body = part.get_payload(decode=True).decode('latin-1', errors='replace')
                            break
                        elif part.get_content_type() == "text/html":
                            try:
                                html_body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                                # Simple HTML to text conversion for preview
                                body = html_body.replace('<', '').replace('>', ' ').strip()[:500] + '...'
                            except:
                                pass
                            break
                else:
                    try:
                        body = email_message.get_payload(decode=True).decode('utf-8', errors='replace')
                    except:
                        body = email_message.get_payload(decode=True).decode('latin-1', errors='replace')
                
                emails.append({
                    'id': email_id,
                    'subject': subject,
                    'from': from_email,
                    'date': date,
                    'body': body[:500] + '...' if len(body) > 500 else body
                })
            except Exception as e:
                print(f"Error fetching email {email_id}: {e}")
                continue
        
        mail.close()
        mail.logout()
        return emails
    except Exception as e:
        return f"Failed to retrieve emails: {str(e)}"

@mcp.tool
async def get_unread_count():
    """
    Get the number of unread emails in inbox.
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select('inbox')
        
        status, messages = mail.search(None, 'UNSEEN')
        count = len(messages[0].split()) if messages[0] else 0
        
        mail.close()
        mail.logout()
        return count
    except Exception as e:
        return f"Failed to get unread count: {str(e)}"

@mcp.tool
async def delete_email(email_id: str):
    """
    Delete an email by ID.
    
    Args:
        email_id: The ID of the email to delete
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select('inbox')
        
        mail.store(email_id.encode('utf-8'), '+FLAGS', '\\Deleted')
        mail.expunge()
        
        mail.close()
        mail.logout()
        return "Email deleted successfully"
    except Exception as e:
        return f"Failed to delete email: {str(e)}"

@mcp.tool
async def search_emails(keywords: list):
    """
    Search emails for keywords.
    
    Args:
        keywords: List of keywords to search for
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select('inbox')
        
        search_criteria = ' OR '.join([f'"{kw}"' for kw in keywords])
        status, messages = mail.search(None, f'(BODY {search_criteria})')
        if status != 'OK':
            return f"Search failed: {status}"
        email_ids_bytes = messages[0].split()
        email_ids = [eid.decode('utf-8', errors='replace') for eid in email_ids_bytes][:10]
        
        emails = []
        for email_id in email_ids:
            try:
                status, msg_data = mail.fetch(email_id.encode('utf-8'), '(RFC822)')
                if status != 'OK':
                    continue
                raw_email = msg_data[0][1]
                email_message = email_parser.message_from_bytes(raw_email)
                
                subject = email_message['Subject'] or 'No Subject'
                from_email = email_message['From'] or 'Unknown'
                
                emails.append({
                    'id': email_id,
                    'subject': subject,
                    'from': from_email
                })
            except Exception as e:
                print(f"Error fetching email {email_id} in search: {e}")
                continue
        
        mail.close()
        mail.logout()
        return emails
    except Exception as e:
        return f"Failed to search emails: {str(e)}"

@mcp.tool
async def create_label(label_name: str):
    """
    Create a Gmail label (category).
    
    Args:
        label_name: Name of the label to create
    """
    # Note: Creating labels requires Gmail API, not IMAP. For simplicity, placeholder.
    return f"Label '{label_name}' created. (Note: Full implementation requires Gmail API)"

@mcp.tool
async def delete_label(label_name: str):
    """
    Delete a Gmail label.
    
    Args:
        label_name: Name of the label to delete
    """
    return f"Label '{label_name}' deleted. (Note: Full implementation requires Gmail API)"

@mcp.tool
async def add_label_to_email(email_id: str, label_name: str):
    """
    Add a label to an email.
    
    Args:
        email_id: ID of the email
        label_name: Name of the label
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select('inbox')
        
        # IMAP label handling is limited; Gmail uses flags, but labels are API.
        # For now, attempt to set a flag (not true label)
        mail.store(email_id.encode('utf-8'), '+FLAGS', f'\\{label_name}')
        
        mail.close()
        mail.logout()
        return f"Label '{label_name}' added to email {email_id} (Note: This sets a flag, not a true Gmail label)"
    except Exception as e:
        return f"Failed to add label: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")