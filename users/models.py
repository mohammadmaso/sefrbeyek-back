from django.db import models
from common.util.mobileValidator import UnicodeMobileNumberValidator


class User(AbstractUser):

    mobile_number_validator = UnicodeMobileNumberValidator()
    phone_number = models.CharField(max_length=50,
                                    unique=True,
                                    verbose_name=_('Mobile Number'),
                                    validators=[mobile_number_validator],
                                    error_messages={
                                        'unique': _("A user with that mobile number already exists."),
                                    },
                                    null=True,
                                    blank=True
                                    )
    email = models.EmailField(
        _('email address'), null=True, blank=True)
    avatar = models.ImageField(blank=True, upload_to='profiles/avatar')

    verified = models.BooleanField(default=False)
    accepted_terms = models.BooleanField(default=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


def sms_expire_time():
    return timezone.now() + timezone.timedelta(seconds=135)


class SMSVerificationCodes(models.Model):
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE)
    code = models.CharField(max_length=8, null=True)
    phone_number = models.CharField(
        null=True, blank=True, validators=[RegexValidator(regex=r"^(/+98)[0-9]{13}$")], max_length=13
    )
    expire_time = models.DateTimeField(default=sms_expire_time)

    def __str__(self):
        return self.user.username
