from .otp_backend import OTPBackend


class ConsolePrintOTPBackend(OTPBackend):
    def send_token(self, receptor, token):
        print(f"printing otp to the console: receptor: {receptor}, token: {token}")
        return True
