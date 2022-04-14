from django.conf import settings
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import serializers
from .exceptions import TokenError, InvalidToken
from .models import OTP, User
from .authentication import AUTH_HEADER_TYPES



# Create your views here.
from .services import TokenService


class RequestOTP(generics.GenericAPIView):
    """
    This returns a N-digit callback token  we can trade for a user's Auth Token.
    """
    permission_classes = (AllowAny,)
    serializer_class = serializers.MobileAuthSerializer
    success_response = _("A login token has been texted to you.")
    failure_response = _("Unable to text you a login code. Try again later.")

    alias_type = 'phone_number'
    token_type = OTP.SMS

    sms_message = settings.AUTHENTICATION['OTP_SMS_MESSAGE']
    message_payload = {
        'sms_message': sms_message,
    }

    def post(self, request, *args, **kwargs):
        # serializer_class = MobileAuthSerializer
        serializer = self.serializer_class(data=request.data, context={'request': request})

        # if serializer is not valid we have raise_exception
        if serializer.is_valid(raise_exception=True):
            # serializer -> validate_data() ->return  attrs -> validated_data
            user = serializer.validated_data['user']

        else:
            return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

        success = TokenService.send_token(user, **self.message_payload)

        if success:
            status_code = status.HTTP_200_OK
            response_detail = self.success_response
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response_detail = self.failure_response

        return Response({'detail': response_detail}, status=status_code)

class TokenViewBase(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = None

    www_authenticate_realm = 'api'

    def get_authenticate_header(self, request):
        return '{0} realm="{1}"'.format(AUTH_HEADER_TYPES[0],
                                        self.www.www_authenticate_realm)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenObtainPairView(TokenViewBase):
    serializer_class = serializers.ConfirmTokenSerializer


token_obtain_pair = TokenObtainPairView.as_view()


class TokenRefreshView(TokenViewBase):
    serializer_class = serializers.TokenRefreshSerializer


token_refresh = TokenRefreshView.as_view()