from django.conf import settings

from .models import User, OTP, Token, VerificationCode
from datetime import timedelta, datetime
from django.utils import timezone



def create_callback_token_for_user(user):
    token = OTP.objects.create(user=user, type=OTP.SMS, is_active=True,
                               exp_date=(timezone.now() +
                                         timedelta(seconds=settings.AUTHENTICATION['OTP_EXPIRE_TIME'])))

    return token