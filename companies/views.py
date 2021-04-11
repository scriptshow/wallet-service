from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from companies.serializers import CompanyRegistrationSerializer
from logging import getLogger

logger = getLogger(__name__)


class CompanyRegistrationView(CreateAPIView):

    """
        CompanyRegistration is a class view used as API endpoint to allow the registration for new companies
    """

    serializer_class = CompanyRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        logger.info("Creating a new Company")
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Company has been created")
        status_code = status.HTTP_201_CREATED
        response = {
            'success': 'True',
            'status_code': status_code,
            'message': "Company registered successfully",
        }

        return Response(response, status=status_code)
