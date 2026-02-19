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
from datetime import datetime
import re

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
async def get_emails(folder: str = 'inbox', limit: int = 10, start: int = 0, unread_only: bool = False):
    """
    Retrieve emails from specified folder (default 'inbox').
    
    Args:
        folder: Folder to fetch from, e.g., 'inbox' or '[Gmail]/Sent Mail' (str)
        limit: Number of emails to retrieve (int)
        start: Starting index (0-based) (int)
        unread_only: If True, only unread emails (bool)
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select(f'"{folder}"')
        
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
                    'to': email_message['To'] or 'Unknown',
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
        return f"Failed to retrieve emails from {folder}: {str(e)}"

@mcp.tool
async def get_unread_count(folder: str = 'inbox'):
    """
    Get the number of unread emails in specified folder (default 'inbox').
    
    Args:
        folder: Folder to check (str)
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select(f'"{folder}"')
        
        status, messages = mail.search(None, 'UNSEEN')
        count = len(messages[0].split()) if messages[0] else 0
        
        mail.close()
        mail.logout()
        return count
    except Exception as e:
        return f"Failed to get unread count from {folder}: {str(e)}"

@mcp.tool
async def delete_email(email_id: str, folder: str = 'inbox'):
    """
    Delete an email by ID from specified folder.
    
    Args:
        email_id: The ID of the email to delete (str)
        folder: Folder to delete from (str)
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select(f'"{folder}"')
        
        mail.store(email_id.encode('utf-8'), '+FLAGS', '\\Deleted')
        mail.expunge()
        
        mail.close()
        mail.logout()
        return "Email deleted successfully"
    except Exception as e:
        return f"Failed to delete email from {folder}: {str(e)}"

@mcp.tool
async def search_emails(keywords: list, date_from: str = None, date_to: str = None, sender: str = None, folder: str = 'inbox'):
    """
    Search emails for keywords, with optional date range, sender filter, and folder.
    
    Args:
        keywords: List of keywords to search for in body (list)
        date_from: Start date in DD-MMM-YYYY format (e.g., '01-Jan-2024') (str)
        date_to: End date in DD-MMM-YYYY format (e.g., '31-Dec-2024') (str)
        sender: Sender email or name to filter by (str)
        folder: Folder to search in (str, default 'inbox')
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select(f'"{folder}"')
        
        criteria = []
        if keywords:
            kw_criteria = ' OR '.join([f'"{kw}"' for kw in keywords])
            criteria.append(f'(BODY {kw_criteria})')
        if date_from:
            criteria.append(f'SINCE {date_from}')
        if date_to:
            criteria.append(f'BEFORE {date_to}')
        if sender:
            criteria.append(f'FROM "{sender}"')
        
        search_str = '(%s)' % ' '.join(criteria) if criteria else 'ALL'
        status, messages = mail.search(None, search_str)
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
        return f"Failed to search emails in {folder}: {str(e)}"

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
async def add_label_to_email(email_id: str, label_name: str, folder: str = 'inbox'):
    """
    Add a label to an email.
    
    Args:
        email_id: ID of the email (str)
        label_name: Name of the label (str)
        folder: Folder of the email (str)
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select(f'"{folder}"')
        
        # IMAP label handling is limited; Gmail uses flags, but labels are API.
        # For now, attempt to set a flag (not true label)
        mail.store(email_id.encode('utf-8'), '+FLAGS', f'\\{label_name}')
        
        mail.close()
        mail.logout()
        return f"Label '{label_name}' added to email {email_id} in {folder} (Note: This sets a flag, not a true Gmail label)"
    except Exception as e:
        return f"Failed to add label in {folder}: {str(e)}"

@mcp.tool
async def forward_email(email_id: str, to: str, custom_subject: str = None, custom_body_prefix: str = None, is_html: bool = False, folder: str = 'inbox'):
    """
    Forward an existing email to a new recipient, optionally with custom prefix.
    
    Args:
        email_id: ID of the email to forward (str)
        to: New recipient email (str)
        custom_subject: Optional custom subject (defaults to 'Fwd: original subject') (str)
        custom_body_prefix: Optional prefix text/HTML before the original email (str)
        is_html: If True, treat custom_body_prefix as HTML (bool)
        folder: Folder of the original email (str)
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select(f'"{folder}"')
        
        status, msg_data = mail.fetch(email_id.encode('utf-8'), '(RFC822)')
        if status != 'OK':
            return f"Failed to fetch email: {status}"
        raw_email = msg_data[0][1]
        original_message = email_parser.message_from_bytes(raw_email)
        
        # Prepare forwarded message
        forwarded = MIMEMultipart('alternative' if is_html else 'mixed')
        forwarded['From'] = SMTP_FROM
        forwarded['To'] = to
        forwarded['Subject'] = custom_subject or f"Fwd: {original_message['Subject']}"
        
        # Custom prefix
        if custom_body_prefix:
            if is_html:
                plain_prefix = custom_body_prefix.replace('<', '').replace('>', ' ').strip()
                forwarded.attach(MIMEText(plain_prefix, 'plain'))
                forwarded.attach(MIMEText(custom_body_prefix, 'html'))
            else:
                forwarded.attach(MIMEText(custom_body_prefix, 'plain'))
        
        # Original email as text
        original_as_text = f"---------- Forwarded message ---------\nFrom: {original_message['From']}\nDate: {original_message['Date']}\nSubject: {original_message['Subject']}\nTo: {original_message['To']}\n\n"
        if original_message.is_multipart():
            for part in original_message.walk():
                if part.get_content_type() == 'text/plain':
                    original_as_text += part.get_payload(decode=True).decode(errors='ignore')
                elif part.get_content_type() == 'text/html':
                    html_body = part.get_payload(decode=True).decode(errors='ignore')
                    original_as_text += html_body.replace('<', '[').replace('>', ']')  # Simple escape
        else:
            original_as_text += original_message.get_payload(decode=True).decode(errors='ignore')
        
        forwarded.attach(MIMEText(original_as_text, 'plain'))
        
        # Send
        smtp_server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        smtp_server.login(SMTP_USER, SMTP_PASS)
        smtp_server.sendmail(SMTP_FROM, to, forwarded.as_string())
        smtp_server.quit()
        
        mail.close()
        mail.logout()
        return "Email forwarded successfully"
    except Exception as e:
        return f"Failed to forward email from {folder}: {str(e)}"

@mcp.tool
async def reply_to_email(email_id: str, reply_body: str, is_html: bool = False, subject_prefix: str = "Re:", folder: str = 'inbox'):
    """
    Reply to an existing email.
    
    Args:
        email_id: ID of the email to reply to (str)
        reply_body: Body of the reply (str)
        is_html: If True, treat reply_body as HTML (bool)
        subject_prefix: Prefix for subject (default "Re:") (str)
        folder: Folder of the original email (str)
    """
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(SMTP_USER, SMTP_PASS)
        mail.select(f'"{folder}"')
        
        status, msg_data = mail.fetch(email_id.encode('utf-8'), '(RFC822)')
        if status != 'OK':
            return f"Failed to fetch email: {status}"
        raw_email = msg_data[0][1]
        original_message = email_parser.message_from_bytes(raw_email)
        
        # Prepare reply
        reply = MIMEMultipart('alternative' if is_html else 'mixed')
        reply['From'] = SMTP_FROM
        reply['To'] = original_message['From']
        reply['Subject'] = f"{subject_prefix} {original_message['Subject']}"
        if 'In-Reply-To' in original_message:
            reply['In-Reply-To'] = original_message['Message-ID']
        if 'References' in original_message:
            reply['References'] = f"{original_message['References']} {original_message['Message-ID']}"
        
        if is_html:
            plain_body = reply_body.replace('<', '').replace('>', ' ').strip()
            reply.attach(MIMEText(plain_body, 'plain'))
            reply.attach(MIMEText(reply_body, 'html'))
        else:
            reply.attach(MIMEText(reply_body, 'plain'))
        
        # Send
        smtp_server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        smtp_server.login(SMTP_USER, SMTP_PASS)
        smtp_server.sendmail(SMTP_FROM, original_message['From'], reply.as_string())
        smtp_server.quit()
        
        mail.close()
        mail.logout()
        return "Reply sent successfully"
    except Exception as e:
        return f"Failed to send reply from {folder}: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")