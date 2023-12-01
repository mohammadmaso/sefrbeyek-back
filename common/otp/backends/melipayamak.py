from .melipayamak_api import Api
from django.conf import settings

from .otp_backend import OTPBackend


# Ref: https://panel.melipayamak.com/Files/webservice-SharedNumber.pdf
class MelipayamakOTPBackend(OTPBackend):
    def send_token(self, receptor, token):
        username = settings.MELIPAYAMAK_USER
        password = settings.MELIPAYAMAK_PASSWORD
        bodyid = settings.MELIPAYAMAK_BODYID
        api = Api(username, password)
        sms_rest = api.sms()
        to = receptor
        sent_sms = sms_rest.send_by_base_number(token, to, bodyid)
        print(sent_sms)
        return sent_sms["RetStatus"] == 1
