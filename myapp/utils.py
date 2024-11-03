# your_app/utils.py
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings

# Function to send SMS via Twilio
def send_sms(phone_number, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )

# Function to send an email
def send_email(email, subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
    
