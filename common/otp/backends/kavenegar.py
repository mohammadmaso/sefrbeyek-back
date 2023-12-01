from django.conf import settings

from kavenegar import KavenegarAPI, APIException, HTTPException
from .otp_backend import OTPBackend


class KavenegarOTPBackend(OTPBackend):
    def send_token(self, receptor, token):
        try:
            api = KavenegarAPI(settings.KAVENEGAR_APIKEY)
            params = {
                'receptor': receptor,
                'template': settings.KAVENEGAR_SMS_TEMPLATE,
                'token': token,
                'type': 'sms'
            }
            response = api.verify_lookup(params)
            print(f"kavenegar sms was sent, response: {response}")
            return True
        except APIException as e:
            print(e)
        except HTTPException as e:
            print(e)
        return False


# def chunks(l, n):
#     """Yield successive n-sized chunks from l."""
#     for i in range(0, len(l), n):
#         yield l[i:i + n]
#
#
# def send_simple_sms(receptors: list, message: str):
#     for receptor_chunks in chunks(receptors, 200):
#         try:
#             api = KavenegarAPI(settings.KAVENEGAR_APIKEY)
#             params = {
#                 'sender': settings.KAVENEGAR_SMS_PHONENUMBER,  # optional
#                 'receptor': [phonenumber.__str__() for phonenumber in receptor_chunks],
#                 # multiple mobile numbers, split by comma
#                 'message': message,
#             }
#             response = api.sms_send(params)
#         except APIException as e:
#             print(e)
#         except HTTPException as e:
#             print(e)
