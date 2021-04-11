from rest_framework import parsers, renderers, status
from rest_framework.authtoken.models import Token
from users.serializers import AuthTokenSerializer
from rest_framework.compat import coreapi, coreschema
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema
from rest_framework.schemas import coreapi as coreapi_schema
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.authentication import ExpiringTokenAuthentication
from walletservice.settings import AUTH_TOKEN_EXPIRATION
from datetime import datetime, timedelta
from pytz import utc
from logging import getLogger

logger = getLogger(__name__)


class ObtainAuthToken(APIView):

    """
        ObtainAuthToken class is used as API endpoint to login and generate an authentication token
    """

    throttle_classes = ()
    permission_classes = (AllowAny,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    if coreapi_schema.is_enabled():
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Username",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        logger.info("User is requesting an auth token")

        status_code = status.HTTP_404_NOT_FOUND
        response = {
            'success': 'False',
            'status code': status_code,
        }

        if 'company' in request.stream.path:
            logger.debug("Using the path for companies")
            if not user.is_company:
                response['message'] = "Company not registered for {0}".format(user)
                logger.info("It's not a company user")
                return Response(response, status=status_code)
        elif 'client' in request.stream.path:
            logger.debug("Using the path for clients")
            if not user.is_client:
                response['message'] = "Client not registered for {0}".format(user)
                logger.info("It's not a client user")
                return Response(response, status=status_code)
        else:
            response['message'] = "Wrong URL path, method only available for client/company"
            logger.warning("It's trying to authenticate outside of companies/clients urls")
            status_code = status.HTTP_400_BAD_REQUEST
            return Response(response, status=status_code)

        token, created = Token.objects.get_or_create(user=user)
        if not created:
            logger.debug("Already exists an auth token for the user, checking if expired")
            # This is required for the time comparison
            utc_now = datetime.utcnow()
            utc_now = utc_now.replace(tzinfo=utc)

            if token.created < utc_now - timedelta(hours=AUTH_TOKEN_EXPIRATION):
                logger.debug("Token has been expired, generating a new one")
                # If token expired, delete it and create a new one
                token.delete()
                token, created = Token.objects.get_or_create(user=user)
            else:
                logger.debug("Token is not expired")
        else:
            logger.debug("A new token has been created")

        logger.info("User has been authenticated, sending the auth token")

        return Response({'token': token.key})


class DestroyAuthToken(APIView):

    """
        DestroyAuthToken class is used as API endpoint to logout and destroy the token in use
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        logger.info("User is requesting to destroy his auth token")
        token = Token.objects.get(user=request.user)
        token.delete()
        logger.info("Auth token has been destroyed")
        return Response(status=status.HTTP_200_OK)
