import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_confirmation_email(email: str, name: str):
    """Send a stylish account creation confirmation email"""
    try:
        # Email content with dynamic name
        subject = "Account Created Successfully"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #4CAF50;">Congratulations, {name}!</h2>
            <p style="font-size: 16px; line-height: 1.6;">
                We are excited to inform you that your account has been successfully created. 
                Welcome aboard! We are thrilled to have you as part of our community.
            </p>
            <p style="font-size: 16px; line-height: 1.6;">
                Now you can easily manage your luggage and track it in real-time through our app. 
                We’ve built a seamless experience for you to enjoy and travel with peace of mind.
            </p>
            <p style="font-size: 16px; line-height: 1.6;">
                Stay tuned for updates and tips on making the most out of your new account. We are committed to providing 
                you with an excellent experience as you travel with us.
            </p>
            <p style="font-size: 16px; line-height: 1.6;">
                If you need any assistance, our support team is always here to help.
            </p>
            <p style="font-size: 16px; line-height: 1.6;">
                Best regards,<br>
                The Luggage Tracker Team
            </p>
            <footer style="font-size: 12px; color: #aaa; text-align: center;">
                <p>If you have any questions, feel free to reply to this email or contact our support team.</p>
                <p>Powered by Luggage Tracker™ | Official Travel Partner</p>
            </footer>
        </body>
        </html>
        """

        # Email setup
        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = email

        # Send email (using Gmail SMTP)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
            server.send_message(msg)
            print(f"Confirmation email sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
