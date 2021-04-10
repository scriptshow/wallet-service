from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from clients.serializers import ClientRegistrationSerializer


class ClientRegistrationView(CreateAPIView):

    """
        ClientRegistration is a class view used as API endpoint to allow the registration for new clients
    """

    serializer_class = ClientRegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        status_code = status.HTTP_201_CREATED
        response = {
            'success': 'True',
            'status_code': status_code,
            'message': 'Client registered successfully',
        }

        return Response(response, status=status_code)
