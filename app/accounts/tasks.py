from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_activation_email_task(user_id, domain, protocol='http'):
    try:
        user = User.objects.get(pk=user_id)
        mail_subject = 'Activate your account.'
        message = render_to_string('accounts/activation_email.html', {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'protocol': protocol,
        })
        to_email = user.email
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()
        return f"Activation email sent to {to_email}"
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found for activation email.")
        return f"User {user_id} not found"
    except Exception as e:
        logger.error(f"Failed to send activation email to user {user_id}: {str(e)}")
        raise e

@shared_task
def send_reset_password_email_task(user_id, domain, protocol='http'):
    try:
        user = User.objects.get(pk=user_id)
        mail_subject = 'Reset your password.'
        message = render_to_string('registration/password_reset_email.html', {
            'user': user,
            'domain': domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'protocol': protocol,
        })
        to_email = user.email
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()
        return f"Reset password email sent to {to_email}"
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found for password reset email.")
        return f"User {user_id} not found"
    except Exception as e:
        logger.error(f"Failed to send reset password email to user {user_id}: {str(e)}")
        raise e
