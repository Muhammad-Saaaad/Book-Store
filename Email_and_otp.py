import random
import smtplib
from email.message import EmailMessage
import time
from database import db_dependency
import model

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()

from_mail = 'saad.cortechsols@gmail.com'

server.login(from_mail ,'uhdm tchd vdxa hmtr')

def generate_otp(user_mail : str):
    otp = ''
    for i in range(6):
        otp += str(random.randint(0,9))
    return otp

    # uhdm tchd vdxa hmtr
def SendEmail(user_mail : str , otp : str):
        to_mail = user_mail
        try:
            msg = EmailMessage()
            msg['subject'] = 'OTP Verification' 
            msg['From'] = from_mail
            msg['To'] = to_mail
            msg.set_content('Your OTP is ' + otp)

            server.send_message(msg)

            print('Email sent')

            return otp
        except:
            return False

# print(generate_otp('rs@gmail.com'))

def thread_function(email : str , db:db_dependency):

    time.sleep(300) # 5 minutes
    
    # check if the email is verified yet or not
    email_data = db.query(model.User).filter(model.User.email == email).first()
    if not email_data.is_verified: # if email is not verified
        db.query(model.User).filter(model.User.email == email).delete(synchronize_session=False)
        db.commit()