import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



smtp_server = 'smtp-mail.outlook.com'
smtp_port = 587
smtp_user = 'your_email@gmail.com'
smtp_password = 'your_password'


def send_email(to_address, subject, body):
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_address
    msg['Subject'] = subject
    body += "Whatever your signature is ### End of Signature" 
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        try:
            server.starttls()
            server.login(smtp_user, smtp_password)
            # yorn = str(input(f"Here's the BODY \n {body}\n Do you want to send it?"))    
            server.send_message(msg)
            return True
        except Exception as e:
            print("Error occured", e)
            

        

