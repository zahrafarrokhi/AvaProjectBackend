from django.conf import settings

from datetime import timedelta, datetime
from django.utils import timezone

from datetime import timedelta, datetime
from calendar import timegm
from datetime import datetime
from django.conf import settings
from django.utils.functional import lazy
from django.utils.timezone import is_naive, make_aware, utc

from authentication.models import OTP


def create_callback_token_for_user(user):
    token = OTP.objects.create(user=user, type=OTP.SMS, is_active=True,
                               exp_date=(timezone.now() +
                                         timedelta(seconds=settings.AUTHENTICATION['OTP_EXPIRE_TIME'])))

    return token


# def create_callback_verification_code_for_user(user, alias, token_type):
#     token = VerificationCode.objects.create(user=user, type=alias,
#                                             exp_date=(timezone.now() +
#                                                       timedelta(seconds=api_settings.OTP_EXPIRE_TIME)))
#
#     return token


def make_utc(dt):
    if settings.USE_TZ and is_naive(dt):
        return make_aware(dt, timezone=utc)

    return dt


def aware_utcnow():
    return make_utc(datetime.utcnow())


def datetime_to_epoch(dt):
    return timegm(dt.utctimetuple())


def datetime_from_epoch(ts):
    return make_utc(datetime.utcfromtimestamp(ts))


def format_lazy(s, *args, **kwargs):
    return s.format(*args, **kwargs)


format_lazy = lazy(format_lazy, str)