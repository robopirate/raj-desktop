"""
gmail.py — Plain Text Email Support Patch
===========================================
This file contains the exact method to add to gmail.py for sending
plain text emails via the Gmail API.

STEP 1: Add send_email_plain() method to the GmailClient class
STEP 2: (Optional) Add create_scheduled_draft_plain() if you need plain text drafts
"""

# ============================================================================
# STEP 1: Add send_email_plain() to GmailClient class
# ============================================================================

# Paste this method into the GmailClient class, after send_email():

    def send_email_plain(self, to, subject, body_text, thread_id=None):
        """Send a plain text email via Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject line
            body_text: Plain text body (no HTML)
            thread_id: Optional Gmail thread ID for threading
            
        Returns:
            dict: Gmail API response with 'id' and 'threadId'
        """
        message = MIMEText(body_text, 'plain', 'utf-8')
        message['to'] = to
        message['subject'] = subject
        if thread_id:
            message['In-Reply-To'] = thread_id
            message['References'] = thread_id
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body = {'raw': raw}
        if thread_id:
            body['threadId'] = thread_id
        return self.service.users().messages().send(userId='me', body=body).execute()


# ============================================================================
# STEP 2: (Optional) Add create_scheduled_draft_plain() for plain text drafts
# ============================================================================

# If you need scheduled drafts in plain text, add this method after
# create_scheduled_draft():

    def create_scheduled_draft_plain(self, to, subject, body_text, send_at_iso):
        """Create a Gmail draft with plain text body and schedule prefix.
        
        The schedule prefix format: [RAJ-SCHEDULE:2026-06-05T10:00:00] Original Subject
        A Google Apps Script can pick these up and send them at the right time.
        """
        scheduled_subject = f"[RAJ-SCHEDULE:{send_at_iso}] {subject}"
        message = MIMEText(body_text, 'plain', 'utf-8')
        message['to'] = to
        message['subject'] = scheduled_subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return self.service.users().drafts().create(userId='me', body={'message': {'raw': raw}}).execute()


# ============================================================================
# STEP 3: (Optional) Add draft_reply_plain() for plain text reply drafts
# ============================================================================

# If reply drafting needs plain text support, add this after draft_reply():

    def draft_reply_plain(self, thread_id, body_text, subject):
        """Create a plain text reply draft in a thread."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['In-Reply-To'] = thread_id
            msg['References'] = thread_id
            msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            body = {'message': {'raw': raw, 'threadId': thread_id}}
            return self.service.users().drafts().create(userId='me', body=body).execute()
        except Exception as e:
            print(f'[Gmail] draft_reply_plain failed: {e}')
            return None
