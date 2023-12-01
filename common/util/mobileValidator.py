import re
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _


@deconstructible
class UnicodeMobileNumberValidator(validators.RegexValidator):
    regex = r'09(\d{9})$'
    message = _(
        'Enter a valid mobile number. This value may contain only numbers.'
    )
    flags = 0


def cellphone_number_validator(phone_number):
    phone_number_regex = re.compile(r'09(\d{9})$')
    return phone_number_regex.match(phone_number)


def phone_number_validator(phone_number):
    phone_number_regex = re.compile(r'021(\d{8})$')
    return phone_number_regex.match(phone_number)


def phone_validator(phone_number):
    """it validates cellphone or phone number"""
    return cellphone_number_validator(phone_number) or phone_number_validator(phone_number)
