from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User
def send_otp_via_email(email):
    subject = f"Your Account Verification Email"
    otp = random.randint(1000,9999)
    email_from = settings.EMAIL_HOST
    message = f"Your Otp is {otp}"
    send_mail(subject,message,email_from,[email])
    user_obj = User.objects.get(email = email)
    user_obj.otp = otp
    user_obj.save()