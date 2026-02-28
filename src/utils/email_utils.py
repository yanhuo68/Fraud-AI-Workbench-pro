import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email using the configured SMTP settings.
    Returns True if successful, False otherwise.
    """
    
    # 1. Check if SMTP is configured
    if not settings.smtp_server or not settings.smtp_sender_email:
        logger.warning("SMTP not configured. Skipping email send.")
        return False

    try:
        # 2. Create message
        message = MIMEMultipart()
        message["From"] = settings.smtp_sender_email
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # 3. Connect and send
        context = ssl.create_default_context()
        
        # Determine strictness based on port/server (simplification: try STARTTLS)
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            # server.set_debuglevel(1) # Uncomment for debug
            server.starttls(context=context)
            
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
                
            server.sendmail(settings.smtp_sender_email, to_email, message.as_string())
            
        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
