import logging
import jwt
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions
from django.utils.translation import ugettext as _

from .token import jwe_decode_handler, jwt_decode_handler, jwe_encode_handler, jwt_encode_handler, generate_jwt_payload, \
    token_decode, token_encode
from user.models import User
logger = logging.getLogger(__name__)


class JSONWebTokenAuthentication(BaseAuthentication):
    """
        Token based authentication using the JSON Web Token standard.
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication. Otherwise returns `None`.
        """
        self.jwe_token = self.get_token_from_header(request)
        if self.jwe_token is None:
            return None

        try:
            payload = token_decode(self.jwe_token)
            user = self.verify_user(payload)
            return user, self.jwe_token
        except jwt.ExpiredSignature:
            if request.META.get('PATH_INFO', None) == '/refresh-token/':
                jwt_token = jwe_decode_handler(self.jwe_token)
                payload = jwt_decode_handler(jwt_token, {'verify_exp': False, })
                auth_user = self.verify_user(payload)
                jwt_payload = generate_jwt_payload(request, auth_user)
                ref_jwt_token = jwt_encode_handler(jwt_payload)
                ref_jwe_token = jwe_encode_handler(ref_jwt_token)
                return auth_user, ref_jwe_token
            logger.info({
                'token': self.jwe_token,
                'message': 'Token has expired',
                'code': 401,
            })
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            logger.exception({
                'token': self.jwe_token,
                'message': 'DecodeError on jwt token.',
                'code': 406,
            })
            msg = _('Error decoding signature')
            raise exceptions.NotAcceptable(msg)
        except jwt.InvalidTokenError:
            logger.exception({
                'token': self.jwe_token,
                'message': 'InvalidTokenError on jwt token.',
                'code': 406,
            })
            raise exceptions.NotAcceptable()

    def get_token_from_header(self, request):
        auth = get_authorization_header(request).split()
        if not auth:
            return None

        elif len(auth) > 1:
            logger.exception({
                'token': self.jwe_token,
                'message': 'Authorization header contains spaces.',
                'code': 403,
            })
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.PermissionDenied(msg)

        return auth[0].decode('utf-8')

    def verify_user(self, payload):
        """
            Return an active user that matches the payload's username.
        """
        user_id = payload.get('user_id')

        if not user_id:
            logger.exception({
                'token': self.jwe_token,
                'message': 'No username found in the token payload',
                'code': 406,
            })
            msg = _('Invalid payload.')
            raise exceptions.NotAcceptable(msg)

        try:
            user = User.objects.get(id=user_id)
            if not user.is_active:
                logger.exception({
                    'token': self.jwe_token,
                    'message': 'User is_active is False',
                    'code': 406,
                })
                msg = _('User account is disabled')
                raise exceptions.NotAcceptable(msg)

        except User.DoesNotExist:
            logger.exception({
                'token': self.jwe_token,
                'message': 'User not present in Database',
                'code': 406,
            })
            msg = _('Invalid signature')
            raise exceptions.NotAcceptable(msg)

        return user
