import random
import re

import graphene
/Users/mohammadmasoudie/Code/Tripper-backend/tripper/user/types.pyfrom django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext as _
from graphene import relay
from graphql_auth import mutations
from graphql_auth.exceptions import GraphQLAuthError
from graphql_auth.types import ExpectedErrorType
from graphql_relay import from_global_id
from graphql import GraphQLError

from common.django_graphene_permission_decorator.mutations import allow_authenticated
from common.otp import send_activation_sms
from .forms import RegisterForm
from .graphene_permissions.mixins import AuthUserMutation
from .graphene_permissions.permissions import AllowAuthenticated
from .inputs import UserInputType
from .models import SMSVerificationCodes
from .types import (UserType)


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    resend_activation_email = mutations.ResendActivationEmail.Field()
    send_password_reset_email = mutations.SendPasswordResetEmail.Field()
    password_reset = mutations.PasswordReset.Field()
    password_set = mutations.PasswordSet.Field()  # For passwordless registration
    update_account = mutations.UpdateAccount.Field()
    archive_account = mutations.ArchiveAccount.Field()
    delete_account = mutations.DeleteAccount.Field()

    verify_token = mutations.VerifyToken.Field()
    refresh_token = mutations.RefreshToken.Field()
    revoke_token = mutations.RevokeToken.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()


class PhoneAlreadyInUse(GraphQLAuthError):
    default_message = _("This phone is already in use.")


class RegisterSMS(graphene.Mutation):
    """Register user and send verification code"""

    success = graphene.Boolean()

    class Arguments:
        phone_number = graphene.String(required=True)
        password1 = graphene.String(required=True)
        password2 = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        try:
            code = random.randrange(1000, 9999, 4)
            f = RegisterForm(kwargs)
            with transaction.atomic():
                if f.is_valid():
                    user = f.save()
                    send_activation_sms(kwargs.get("phone_number"), code)
                    SMSVerificationCodes.objects.create(user=user, code=code)
                else:
                    raise GraphQLError(f.errors.get_json_data())

                return RegisterSMS(success=True)

        except PhoneAlreadyInUse:
            raise GraphQLError(_('This phone is already in use.'))


class VerifySMS(graphene.Mutation):
    """Verify user using verification code that send with sms"""

    success = graphene.Boolean()

    class Arguments:
        code = graphene.String(required=True)
        phone_number = graphene.String(required=True)

    @classmethod
    def mutate(cls, info, root, phone_number, code, **kwargs):
        user = get_user_model().objects.filter(phone_number=phone_number)
        if not user.exists():
            raise GraphQLError(_('User is invalid'))
        user = user[0]

        saved_code = SMSVerificationCodes.objects.filter(user=user)
        if not saved_code.exists():
            raise GraphQLError(_('User not created, Register again'))
        saved_code = saved_code[0]

        if saved_code.code == code and saved_code.expire_time > timezone.now():
            user.verified = True
            user.save()
            return VerifySMS(success=True)
        raise GraphQLError(_('your confirm code is expired or incorrect...'))


class ResendVerificationSMS(graphene.Mutation):
    """Resend sms to user"""
    success = graphene.Boolean()

    class Arguments:
        phone_number = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, phone_number):
        user = get_user_model().objects.filter(phone_number=phone_number)
        if not user.exists():
            raise GraphQLError(_('User is invalid'))
        user = user[0]

        code = random.randrange(1000, 9999, 4)
        SMSVerificationCodes.objects.filter(user=user)[0].delete()
        send_activation_sms(phone_number, code)
        SMSVerificationCodes.objects.create(user=user, code=code)

        return ResendVerificationSMS(success=True)


class ForgotPasswordSMS(graphene.Mutation):
    """send forgotten passworld sms verification"""

    success = graphene.Boolean()

    class Arguments:
        phone_number = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, phone_number):
        user = get_user_model().objects.filter(phone_number=phone_number)
        if not user.exists():
            raise GraphQLError(_('User is invalid'))
        user = user[0]

        code = random.randrange(1000, 9999, 4)
        SMSVerificationCodes.objects.filter(user=user).delete()
        send_activation_sms(phone_number, code)
        SMSVerificationCodes.objects.create(user=user, code=code)

        return ForgotPasswordSMS(success=True)


class ResetPasswordSMS(graphene.Mutation):
    """reset password"""

    success = graphene.Boolean()

    class Arguments:
        phone_number = graphene.String(required=True)
        code = graphene.String(required=True)
        new_password1 = graphene.String(required=True)
        new_password2 = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        code = kwargs.get("code")
        new_password1 = kwargs.get("new_password1")
        new_password2 = kwargs.get("new_password2")
        phone_number = kwargs.get("phone_number")

        if not new_password1 == new_password2:
            raise GraphQLError(_('password1 is not equal to password2.'))

        user = get_user_model().objects.filter(phone_number=phone_number)
        if not user.exists():
            raise GraphQLError(_('User is invalid.'))
        user = user[0]

        saved_code = SMSVerificationCodes.objects.filter(user=user)
        if not saved_code.exists():
            raise GraphQLError(_('try again.'))
        else:
            saved_code = saved_code[0]
            if not saved_code == code:
                raise GraphQLError(_('entered code is wrong.'))

        form = SetPasswordForm(user, kwargs)
        if form.is_valid():
            user = form.save()
            saved_code.delete()
        else:
            raise GraphQLError(form.errors.get_json_data())

        return ResetPasswordSMS(success=True)


class UpdateUser(relay.ClientIDMutation):
    class Input:
        userInputs = graphene.Field(UserInputType)

    user = graphene.Field(UserType)

    @classmethod
    @allow_authenticated
    def mutate_and_get_payload(cls, root, info, userInputs):
        user = info.context.user
        for (key, value) in userInputs.items():
            if (value is not None):
                setattr(user, key, value)
        user.save()
        return UpdateUser(user=user)


class ChangePasswordMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Input:
        old_password = graphene.String(required=True)
        new_password1 = graphene.String(required=True)
        new_password2 = graphene.String(required=True)

    @classmethod
    @allow_authenticated
    def mutate(cls, root, info, old_password, new_password1, new_password2):
        user = info.context.user
        if check_password(password=old_password, encoded=user.password):
            if new_password1 == new_password2:
                validate_password(new_password1)
                user.set_password(new_password1)
                user.save()
                return ChangePasswordMutation(success=True)
            raise GraphQLError(_('password1 and password2 are not the same.'))
        raise GraphQLError(_('password is incorrect.'))



class ChangePhoneNumberFirstStepMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Input:
        phone_number = graphene.String(required=True)

    @classmethod
    @allow_authenticated
    def mutate(cls, root, info, phone_number):
        user = info.context.user
        compiled_regex = re.compile("^(/+98)[0-9]{13}$")
        if compiled_regex.match(phone_number):
            sms_verification = SMSVerificationCodes.objects.filter(user=user, expire_time__lte=timezone.now())
            if not sms_verification.exists():
                user_with_phone_number = get_user_model().objects.filter(phone_number=phone_number)
                if not user_with_phone_number.exists():
                    code = random.randrange(1000, 9999)
                    SMSVerificationCodes.objects.create(user=user, code=code)
                    send_activation_sms(phone_number, code)
                    return ChangeUsernameMutation(success=True)
                raise GraphQLError(_('user with this phone number exists.'))
            raise GraphQLError(_("user can't send verification code under two minutes."))
        raise GraphQLError(_('invalid phone number.'))


class ChangePhoneNumberSecondStepMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        code = graphene.String(required=True)
        phone_number = graphene.String(required=True)

    @classmethod
    @allow_authenticated
    def mutate(cls, root, info, phone_number):
        user = info.context.user
        sms_verification = SMSVerificationCodes.objects.filter(
            user=user, expire_time__lte=timezone.now(), phone_number=phone_number
        )
        if sms_verification.exists():
            user.phone_number = phone_number
            user.save()
            sms_verification[0].delete()
        raise GraphQLError(_('invalid phone number or your code expired.'))


class Mutation(AuthMutation, graphene.ObjectType):
    update_user = UpdateUser.Field()
    register_sms = RegisterSMS.Field()
    verify_sms = VerifySMS.Field()
    resend_verification_sms = ResendVerificationSMS.Field()
    reset_password_sms = ResetPasswordSMS.Field()
    forgot_password_sms = ForgotPasswordSMS.Field()
    password_change = ChangePasswordMutation.Field()
