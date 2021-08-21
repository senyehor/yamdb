from uuid import uuid4

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail as send_ml
from django.core.validators import validate_email
from rest_framework_simplejwt.tokens import RefreshToken

from api.errors import EmailNotValid
from api.models import EmailCode, Review, User
from api_yamdb import settings


def send_email(subject: str, content: str, email: str):
    try:
        validate_email(email)
        send_ml(subject, content, settings.EMAIL_HOST_USER, [email])
    except ValidationError:
        raise EmailNotValid


def generate_code():
    return str(uuid4())


def send_code_to_user_and_save_it(user_email: str):
    code = generate_code()
    send_email('Registration code', f'Your code is {code}', user_email)
    email_code_object, created = EmailCode.objects.get_or_create(email=user_email)
    email_code_object.code = code
    email_code_object.save()


def user_already_has_review_on_title(author, title):
    return Review.objects.filter(author=author, title=title).exists()


def get_code_if_email_was_sent_else_none(email):
    try:
        email_code_object = EmailCode.objects.get(email=email)
    except ObjectDoesNotExist:
        return None
    return email_code_object.code


def create_token_for_user_by_email(email):
    token = RefreshToken.for_user(User.objects.get(email=email))
    return {'access': token.access_token, 'refresh': str(token)}


def check_data_contains_only_allowed_to_modify_fields(data):
    return all(map(lambda field_to_change_name: field_to_change_name in User.ALLOWED_FIELDS_TO_FILL, data))
