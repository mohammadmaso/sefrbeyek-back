from importlib import import_module
from django.conf import settings

from common.otp.backends.otp_backend import OTPBackend


def load_class(import_path):
    names = import_path.split('.')
    module_name = '.'.join(names[:-1])
    class_name = names[-1]

    module = import_module(module_name)
    return getattr(module, class_name)


def send_activation_sms(receptor, token):
    otp_backend = load_class(settings.OTP_BACKEND)
    return otp_backend().send_token(receptor, token)
