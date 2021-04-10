from rest_framework.authentication import TokenAuthentication  # get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from walletservice.settings import AUTH_TOKEN_EXPIRATION
from datetime import datetime, timedelta
from pytz import utc


class ExpiringTokenAuthentication(TokenAuthentication):

    """
        Custom TokenAuthentication, extending the TokenAuthentication model adding the expiration of the token
    """

    def authenticate_credentials(self, key):
        try:
            token = self.get_model().objects.get(key=key)
        except self.get_model().DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted')

        # This is required for the time comparison
        utc_now = datetime.utcnow()
        utc_now = utc_now.replace(tzinfo=utc)

        if token.created < utc_now - timedelta(hours=AUTH_TOKEN_EXPIRATION):
            raise AuthenticationFailed('Token has expired')

        return token.user, token
