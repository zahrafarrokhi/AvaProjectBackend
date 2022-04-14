from django.conf import settings

from authentication.utils import create_callback_token_for_user
import requests


class TokenService(object):
    @staticmethod
    def send_token(user, **message_payload):
        token = create_callback_token_for_user(user)
        send_action = None
        success = False

        return True


class SMSPanelService:
    @staticmethod
    #  def send_sms(mobile, text, body_id, is_flash=True):
    def send_sms(mobile, args, body_id, is_flash=True):
        payload = {
            'to': mobile,
            'args': args,
            'bodyId': int(body_id),
        }

        try:
            response = requests.post(
                f'https://console.melipayamak.com/api/send/shared/{settings.SMS["SMS_PANEL_TOKEN"]}',
                json=payload)

            res = response.json()

            # if len(str(res['recId'])) < 15:
            #     logger.error("Failed to send SMS, Invalid recId", extra={'result': res,
            #                                                              'sms_payload': payload})

            return len(str(res['recId'])) >= 15
        except Exception as e:
            # logger.error("Failed to send SMS", extra={'sms_payload': payload})
            # logger.exception(e)
            return False