import requests
import json
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

class SendGridAPIBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0
            
        api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        if not api_key:
            return 0
            
        sent_count = 0
        for message in email_messages:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Recipient list
            to_emails = [{"email": r} for r in message.to]
            personalizations = [{"to": to_emails}]
            
            # Content list
            content = []
            if message.body:
                content.append({"type": "text/plain", "value": message.body})
                
            # Check for HTML content
            # Django's EmailMultiAlternatives stores html in message.alternatives
            for alt in getattr(message, 'alternatives', []):
                if len(alt) >= 2 and alt[1] == 'text/html':
                    content.append({"type": "text/html", "value": alt[0]})
                    
            # Fallback if no content
            if not content:
                content.append({"type": "text/plain", "value": " "})
                
            # From email address parsing
            from_email_addr = message.from_email
            from_name = "Stack Teller Trust Bank"
            if "<" in from_email_addr and ">" in from_email_addr:
                parts = from_email_addr.split("<")
                from_name = parts[0].strip()
                from_email_addr = parts[1].replace(">", "").strip()
                
            data = {
                "personalizations": personalizations,
                "from": {"email": from_email_addr, "name": from_name},
                "subject": message.subject,
                "content": content
            }
            
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
                if response.status_code == 202:
                    sent_count += 1
            except Exception:
                pass
                
        return sent_count
