import functools
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

module_logger = logging.getLogger('woof_reporter.sender')


def reconnect(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            rv = func(self, *args, **kwargs)
        except (TimeoutError, Exception) as e:
            self.logger.debug(e, exc_info=True)
            self.s = smtplib.SMTP(host=self.host, port=self.port)
            self.s.starttls()
            self.s.login(self.address, self._password)
            self.logger.info('Reconnected to {} server at port {}'.format(self.host, self.port))
            rv = func(self, *args, **kwargs)
        finally:
            return rv

    return wrapper


class EmailSender:
    def __init__(self):
        self.logger = logging.getLogger('woof_reporter.sender.EmailSender')
        self.host = os.environ.get('EMAIL_HOST')
        self.port = int(os.environ.get('EMAIL_PORT'))
        self.address = os.environ.get('EMAIL_ADDRESS')
        self._password = os.environ.get('EMAIL_PASSWORD')
        self.s = smtplib.SMTP(host=self.host, port=self.port)
        self.s.starttls()
        self.s.login(self.address, self._password)
        self.to_list = str(os.environ.get('EMAIL_LIST')).split(',')
        self.logger.debug('EmailSender class initialized')

    @reconnect
    def send_message(self, subject, message):
        for email in self.to_list:
            msg = MIMEMultipart()
            msg['From'] = self.address
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            self.s.send_message(msg)
            self.logger.info(
                'Message send:\n'
                '\tFrom - {}\n'
                '\tTo - {}\n'
                '\tSubject - {}\n'
                '\tMessage - {}'.format(self.address, self.to_list, subject, message)
            )

            del msg
        return True

    @reconnect
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
            self.logger.info(
                'Message send:\n'
                '\tFrom - {}\n'
                '\tTo - {}\n'
                '\tSubject - {}\n'
                '\tMessage - {}\n'
                '\tAttachment - {}'.format(self.address, self.to_list, subject, message, file_path)
            )

            del msg
        return True
