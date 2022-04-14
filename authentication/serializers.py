from django.conf import settings
from django.core.validators import RegexValidator
from django.utils import timezone
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from authentication.models import User, OTP, Token
from authentication.tokens import AccessToken


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


class ConfirmTokenSerializer(serializers.Serializer):
    phone_regex = RegexValidator(
        regex=r'^\d{10,16}$', message=_("Invalid Mobile Number"))
    phone_number = serializers.CharField(
        validators=[phone_regex], max_length=17, required=False)

    token = TokenField(min_length=settings.AUTHENTICATION['OTP_LENGTH'], max_length=settings.AUTHENTICATION['OTP_LENGTH'])
    user = UserSerializer(many=False, read_only=True)


    def validate(self, attrs):
        try:
            callback_token = attrs.get('token', None)

            user = User.objects.get(phone_number=attrs['phone_number'])

            token = OTP.objects.get(
                user=user,
                value=callback_token,
                is_active=True,
            )
            if token.exp_date < timezone.now():
                token.is_active = False
                token.save()
                msg = _('Invalid Token')
                raise serializers.ValidationError(msg)

            if not user.is_active:
                msg = _('User account is disabled')
                raise serializers.ValidationError(msg)

            if user.phone_number_verified is False:
                user.phone_number_verified = True
                user.save()

            token.is_active = False
            token.save()

            attrs['user'] = UserSerializer(user).data


            access_token = AccessToken.for_user(user)
            refresh_token = (Token.objects.
                             create(user=user,
                                    exp_date=timezone.now() +
                                             settings.AUTHENTICATION['REFRESH_TOKEN_LIFETIME']))

            attrs['access_tok'] = str(access_token)
            attrs['refresh_tok'] = refresh_token.tokenid
            attrs['refresh_tok_exp'] = refresh_token.exp_date
            attrs['access_tok_exp'] = access_token.get_exp()

            return attrs

        except OTP.DoesNotExist:
            msg = _('Invalid alias parameters provided.')
            raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            msg = _('Invalid user alias parameters provided')
            raise serializers.ValidationError(msg)
        except ValidationError:
            msg = _('Invalid ailas parameters provided.')
            raise serializers.ValidationError(msg)




class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    user_id = serializers.CharField()
    access = serializers.ReadOnlyField()

    def validate(self, attrs):
        data = {}
        print("Refreshing token")
        try:
            ref = Token.objects.get(
                tokenid=attrs['refresh'],
                user=User.objects.get(phone_number=attrs['user_id']))
            if ref.exp_date < timezone.now():
                msg = _("Refresh token has expired")
                raise serializers.ValidationError(msg)
            user = User.objects.get(pk=ref.user.id)
            tok = AccessToken.for_user(user)  # Create JWT
            data['access_tok'] = str(tok)
            data['access_tok_exp'] = tok.get_exp()
        except Token.DoesNotExist:
            msg = _('Invalid token')
            raise serializers.ValidationError(msg)
        except User.DoesNotExist:
            msg = _('Invalid token')
            raise serializers.ValidationError(msg)

        return data