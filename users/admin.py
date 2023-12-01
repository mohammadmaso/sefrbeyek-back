from django.contrib import admin
from .models import User, SMSVerificationCodes


class UserAdmin(UserAdmin):
    model = User


class SMSVerificationAdmin(admin.ModelAdmin):
    readonly_fields = ('expire_time', )

    class Meta:
        model = SMSVerificationCodes


admin.site.register(User, UserAdmin)
admin.site.register(SMSVerificationCodes, SMSVerificationAdmin)
