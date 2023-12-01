from importlib import import_module

from django.test import TestCase, override_settings
from django.conf import settings
from unittest.mock import patch

from common.otp import send_activation_sms


class OTPBackendTest(TestCase):
    def setUp(self):
        self.receptor = "09369203318"
        self.token = "123456"

    @override_settings(OTP_BACKEND='common.otp.backends.console_print.ConsolePrintOTPBackend')
    @patch('builtins.print')
    def test_console_print(self, mock_print):
        result = send_activation_sms(self.receptor, self.token)
        self.assertTrue(result)

        mock_print.assert_called_with(
            f"printing otp to the console: receptor: {self.receptor}, token: {self.token}")

    @override_settings(OTP_BACKEND='common.otp.backends.melipayamak.MelipayamakOTPBackend')
    @patch('common.otp.backends.melipayamak.Api')
    def test_melipayamak(self, mock_Api):
        mock_Api().sms().send_by_base_number.return_value = {'RetStatus': 1}

        result = send_activation_sms(self.receptor, self.token)
        self.assertTrue(result)

        mock_Api().sms().send_by_base_number.assert_called_with(
            self.token, self.receptor, settings.MELIPAYAMAK_BODYID)

    @override_settings(OTP_BACKEND='common.otp.backends.kavenegar.KavenegarOTPBackend')
    def test_kavenegar(self):
        pass  # this backend has never been used and thus not tested
