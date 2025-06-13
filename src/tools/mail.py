import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formatdate
import os
import logging

logger = logging.getLogger(__name__)


class Email:
    def __init__(self, password=None):
        """Initialize the Email class with an optional password."""
        self.password = password

    def set_password(self, password):
        """Set the email account password."""
        self.password = password

    def send_email(self, subject, body, to_email, from_email, smtp_port=587):
        """Send a simple email."""
        smtp_server = self.smtp_server
        if not self.password:
            raise ValueError("Email password not set. Use set_password() first.")

        msg = MIMEText(body)
        msg["Subject"] = msg.get("Subject", "")
        msg["From"] = msg.get("From", from_email)
        msg["To"] = msg.get("To", to_email)
        msg["Date"] = formatdate(localtime=True)

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(from_email, self.password)
                server.send_message(msg)
            print(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.info("Failed to send email")
            return False

    def send_email_with_attachment(
        self,
        subject,
        body,
        to_email,
        from_email,
        attachment_path=None,
        smtp_server="smtp.gmail.com",
        smtp_port=587,
    ):
        """Send email with optional attachment."""
        if not self.password:
            raise ValueError("Email password not set. Use set_password() first.")

        msg = MIMEMultipart()
        msg["Subject"] = msg.get("Subject", subject)
        msg["From"] = msg.get("From", from_email)
        msg["To"] = msg.get("To", to_email)
        msg["Date"] = formatdate(localtime=True)
        msg.attach(MIMEText(body))

        if attachment_path:
            if not os.path.exists(attachment_path):
                raise FileNotFoundError(f"Attachment not found: {attachment_path}")

            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(attachment_path)}"'
            )
            msg.attach(part)

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(from_email, self.password)
                server.send_message(msg)
            print(f"Email with attachment sent to {to_email}")
            return True
        except Exception as e:
            logger.info("Failed to send email with attachment")
            return False
