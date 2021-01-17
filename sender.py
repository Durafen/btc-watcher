import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import keyring
import getpass
import configparser
import debug

config = configparser.ConfigParser()
config.read("config.txt")

FROM_EMAIL = str(config.get('smtp', 'FROM_EMAIL'))
TO_EMAIL = str(config.get('smtp', 'TO_EMAIL'))
IS_SMTP_ENABLED = int(config.get('smtp', 'IS_SMTP_ENABLED'))

if IS_SMTP_ENABLED:
    if not keyring.get_password("gmail_sender", FROM_EMAIL):
        keyring.set_password("gmail_sender", FROM_EMAIL, getpass.getpass('Password:'))
    sender_pass = keyring.get_password("gmail_sender", FROM_EMAIL)

mail_content = ' '


def send_email(price):
    if IS_SMTP_ENABLED:
        message = MIMEMultipart()
        message['From'] = FROM_EMAIL
        message['To'] = TO_EMAIL
        message['Subject'] = 'BTC - ' + price
        message.attach(MIMEText(mail_content, 'plain'))

        try:
            session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
            session.starttls()
            session.login(FROM_EMAIL, sender_pass)

            text = message.as_string()
            session.sendmail(FROM_EMAIL, TO_EMAIL, text)
            session.quit()
        except Exception as e:
            debug.output_error(e)


if __name__ == '__main__':
    send_email("test")
#    print ("test")
