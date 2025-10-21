# Example: Email connections
import smtplib
from email.mime.text import MIMEText

# SMTP connection
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("test@gmail.com", "password")

# Send email
msg = MIMEText("Test message")
msg['Subject'] = "Test"
msg['From'] = "test@gmail.com"
msg['To'] = "recipient@example.com"
server.sendmail("test@gmail.com", "recipient@example.com", msg.as_string())
server.quit()
