from django.conf import settings

from .backends import TokenBackend

token_backend = TokenBackend(
    settings.AUTHENTICATION['ALGORITHM'],
    settings.AUTHENTICATION['SIGNING_KEY'],
    settings.AUTHENTICATION['VERIFYING_KEY'],
    settings.AUTHENTICATION['AUDIENCE'],
    settings.AUTHENTICATION['ISSUER'],
    settings.AUTHENTICATION['JWK_URL'],
)