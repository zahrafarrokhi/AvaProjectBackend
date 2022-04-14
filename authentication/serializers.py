from django.core.validators import RegexValidator
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from authentication.models import User, OTP


class TokenField(serializers.CharField):
    default_error_messages = {
        'required': _('Invalid Token'),
        'invalid': _('Invalid Token'),
        'blank': _('Invalid Token'),
        'max_length': _('Tokens are {max_length} digits long.'),
        'min_length': _('Tokens are {min_length} digits long.')
    }




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number',  'phone_number_verified', 'type']



class MobileAuthSerializer(serializers.Serializer):
    phone_regex = RegexValidator(
        regex=r'^\d{10,16}$', message=_("Invalid Mobile Number"))
    phone_number = serializers.CharField(
        validators=[phone_regex], max_length=17)

    def validate(self, attrs):
        # all of serializer fields are in attrs
        phone_number = attrs['phone_number']

        # get user if user doesnt exist create user [get,create,otp filter and bulk_update]
        try:
            user = User.objects.get(phone_number=phone_number)

            # Deactive all active OTPs for this user
            previous_tokens = OTP.objects.filter(
                user=user, is_active=True)
            print(previous_tokens)

            for tok in previous_tokens:
                tok.is_active = False
            # use bulk_update for saving all tokens at the same time
            OTP.objects.bulk_update(previous_tokens, ['is_active'])

        #     user doesnot exist create this user with phone
        except User.DoesNotExist:
            user = User.objects.create(phone_number=phone_number)
            user.set_unusable_password()
            user.save()

        attrs['user'] = user
        # if user is not active
        if not user.is_active:
            msg = _('This account is disabled.')
            raise serializers.ValidationError(msg)

        return attrs
