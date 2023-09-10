from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_verification_email(request, user, email_subject, email_template):
    email_body = render_to_string(
        template_name=email_template,
        context={
            'user': user,
            'domain': get_current_site(request),
            'uidb64': urlsafe_base64_encode(force_bytes(user.id)),
            'token': default_token_generator.make_token(user),
        }
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email
    EmailMessage(email_subject, email_body, from_email, [to_email]).send()
