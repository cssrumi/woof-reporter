import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class EmailSender:
    def __init__(self):
        self.host = os.environ.get('EMAIL_HOST')
        self.port = int(os.environ.get('EMAIL_PORT'))
        self.address = os.environ.get('EMAIL_ADDRESS')
        password = os.environ.get('EMAIL_PASSWORD')
        self.s = smtplib.SMTP(host=self.host, port=self.port)
        self.s.starttls()
        self.s.login(self.address, password)
        self.to_list = str(os.environ.get('EMAIL_LIST')).split(',')

    def send_message(self, subject, message):
        for email in self.to_list:
            msg = MIMEMultipart()
            msg['From'] = self.address
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            self.s.send_message(msg)

            del msg

    def send_message_with_attachments(self, subject, message, file_path):
        for email in self.to_list:
            msg = MIMEMultipart()
            msg['From'] = self.address
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            attachment = open(file_path, 'rb')

            # instance of MIMEBase and named as p
            p = MIMEBase('application', 'octet-stream')

            # To change the payload into encoded form
            p.set_payload((attachment).read())

            # encode into base64
            encoders.encode_base64(p)

            filename = os.path.basename(file_path)
            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            # attach the instance 'p' to instance 'msg'
            msg.attach(p)

            text = msg.as_string()

            self.s.sendmail(self.address, email, text)

            del msg
