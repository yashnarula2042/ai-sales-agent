import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    def send_email(self, to_email, subject, body):
        if not self.smtp_user or "your_email" in self.smtp_user:
            return False, "SMTP_USER is not configured in .env"
        
        if not self.smtp_password or "your_app_password" in self.smtp_password:
            return False, "SMTP_PASSWORD is not configured in .env"

        message = MIMEMultipart()
        message["From"] = self.smtp_user
        message["To"] = to_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, to_email, message.as_string())
            logger.info(f"Email sent successfully to {to_email}")
            return True, "Sent"
        except Exception as e:
            err_msg = str(e)
            logger.error(f"Failed to send email to {to_email}: {err_msg}")
            return False, err_msg
