from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field, EmailStr
from services.redis_service import redis_service
from config.settings import settings
import resend
from datetime import datetime


class SendEmailInput(BaseModel):
    """Input for Send Email"""
    user_id: str = Field(..., description="User ID for rate limiting")
    to_email: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body (HTML or plain text)")
    from_name: str = Field(default="CareerOS", description="Sender name")


class SendEmailTool(BaseTool):
    name: str = "Send Email"
    description: str = """Send an email to a contact. Checks rate limits and logs the activity. 
    Use this after getting approval for outreach messages."""
    args_schema: Type[BaseModel] = SendEmailInput
    
    def _run(
        self,
        user_id: str,
        to_email: str,
        subject: str,
        body: str,
        from_name: str = "CareerOS"
    ) -> str:
        try:
            # Check rate limit
            allowed, count = redis_service.check_rate_limit(
                user_id,
                "email_sent",
                settings.EMAIL_DAILY_LIMIT
            )
            
            if not allowed:
                return f"❌ Email rate limit exceeded. Daily limit: {settings.EMAIL_DAILY_LIMIT}"
            
            # Validate email
            if not to_email or '@' not in to_email:
                return "❌ Invalid email address"
            
            if not subject or not body:
                return "❌ Subject and body are required"
            
            # Check if Resend API key is configured
            if not settings.RESEND_API_KEY:
                # Development mode - simulate sending
                output = f"📧 Email queued (Development Mode):\n\n"
                output += f"To: {to_email}\n"
                output += f"From: {from_name}\n"
                output += f"Subject: {subject}\n"
                output += f"Body Preview: {body[:100]}...\n\n"
                output += f"Rate limit: {count}/{settings.EMAIL_DAILY_LIMIT} emails today\n"
                output += f"\nNote: Configure RESEND_API_KEY to actually send emails."
                return output
            
            # Initialize Resend
            resend.api_key = settings.RESEND_API_KEY
            
            # Send email
            email = resend.Emails.send({
                "from": f"{from_name} <noreply@yourdomain.com>",
                "to": to_email,
                "subject": subject,
                "html": body if "<html>" in body.lower() else f"<p>{body}</p>"
            })
            
            output = f"✅ Email sent successfully!\n\n"
            output += f"To: {to_email}\n"
            output += f"Subject: {subject}\n"
            output += f"Email ID: {email.get('id', 'N/A')}\n"
            output += f"Rate limit: {count}/{settings.EMAIL_DAILY_LIMIT} emails today"
            
            return output
            
        except Exception as e:
            return f"❌ Error sending email: {str(e)}"


class EmailTemplateInput(BaseModel):
    """Input for Email Template"""
    template_type: str = Field(..., description="Type of template: cold_email, follow_up, thank_you")
    recipient_name: str = Field(..., description="Recipient's name")
    personalization_data: dict = Field(..., description="Data for personalizing the template")


class EmailTemplateTool(BaseTool):
    name: str = "Generate Email Template"
    description: str = """Generate a professional email template based on type and personalization data. 
    Returns a formatted email ready to be reviewed and sent."""
    args_schema: Type[BaseModel] = EmailTemplateInput
    
    def _run(
        self,
        template_type: str,
        recipient_name: str,
        personalization_data: dict
    ) -> str:
        try:
            if template_type == "cold_email":
                template = self._cold_email_template(recipient_name, personalization_data)
            elif template_type == "follow_up":
                template = self._follow_up_template(recipient_name, personalization_data)
            elif template_type == "thank_you":
                template = self._thank_you_template(recipient_name, personalization_data)
            else:
                return "Invalid template type. Use: cold_email, follow_up, or thank_you"
            
            return template
            
        except Exception as e:
            return f"Error generating template: {str(e)}"
    
    def _cold_email_template(self, name: str, data: dict) -> str:
        subject = data.get('subject', f"Question about {data.get('their_work', 'your work')}")
        
        body = f"""Subject: {subject}

Hi {name},

{data.get('opening', f"I came across your work on {data.get('their_work', 'LinkedIn')} and was really impressed.")}

{data.get('connection_point', 'I noticed we share an interest in similar areas.')}

{data.get('user_background', 'I recently worked on a related project where...')}

{data.get('ask', 'Would you be open to a brief 15-minute call to discuss this further?')}

{data.get('closing', 'Thanks for considering, and I hope to hear from you!')}

Best regards,
{data.get('user_name', 'Your Name')}
{data.get('user_title', '')}
{data.get('user_contact', '')}
"""
        return body
    
    def _follow_up_template(self, name: str, data: dict) -> str:
        subject = f"Re: {data.get('original_subject', 'Following up')}"
        
        body = f"""Subject: {subject}

Hi {name},

I wanted to follow up on my message from {data.get('days_ago', '7')} days ago about {data.get('topic', 'connecting')}.

{data.get('new_info', 'Since reaching out, I also wanted to mention...')}

{data.get('gentle_ask', 'I understand you might be busy, but I would still love to connect when you have a moment.')}

{data.get('closing', 'Thanks again for your time!')}

Best regards,
{data.get('user_name', 'Your Name')}
"""
        return body
    
    def _thank_you_template(self, name: str, data: dict) -> str:
        subject = f"Thank you for {data.get('reason', 'your time')}"
        
        body = f"""Subject: {subject}

Hi {name},

Thank you so much for {data.get('reason', 'taking the time to speak with me')}.

{data.get('specific_takeaway', 'I really appreciated your insights on...')}

{data.get('action_item', 'As discussed, I will...')}

{data.get('closing', 'Looking forward to staying in touch!')}

Best regards,
{data.get('user_name', 'Your Name')}
"""
        return body


class CheckEmailStatusInput(BaseModel):
    """Input for Check Email Status"""
    email_id: str = Field(..., description="Email ID from Resend")


class CheckEmailStatusTool(BaseTool):
    name: str = "Check Email Status"
    description: str = """Check the delivery status of a sent email. 
    Returns whether it was delivered, opened, or bounced."""
    args_schema: Type[BaseModel] = CheckEmailStatusInput
    
    def _run(self, email_id: str) -> str:
        try:
            if not settings.RESEND_API_KEY:
                return "Email status tracking requires RESEND_API_KEY to be configured."
            
            resend.api_key = settings.RESEND_API_KEY
            
            # Get email status
            email = resend.Emails.get(email_id)
            
            output = f"Email Status Report:\n\n"
            output += f"ID: {email.get('id')}\n"
            output += f"To: {email.get('to')}\n"
            output += f"Subject: {email.get('subject')}\n"
            output += f"Status: {email.get('status')}\n"
            output += f"Created: {email.get('created_at')}\n"
            
            if email.get('last_event'):
                output += f"\nLast Event: {email['last_event']}\n"
            
            return output
            
        except Exception as e:
            return f"Error checking email status: {str(e)}"
