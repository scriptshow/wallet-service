from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from clients.models import Client
from users.models import User


class ClientSerializer(serializers.ModelSerializer):

    """
        Default Client serializer
    """

    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'phone_number')


class ClientRegistrationSerializer(serializers.ModelSerializer):

    """
        ClientRegistration serializer used to sign up new clients
    """

    client = ClientSerializer(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'client')
        extra_kwargs = {'password': {'write_only': True, 'validators': [validate_password, ]}}

    def create(self, validated_data):
        client_data = validated_data.pop('client')
        user = User.objects.create_client(**validated_data)
        Client.objects.create(
            user=user,
            first_name=client_data['first_name'],
            last_name=client_data['last_name'],
            phone_number=client_data['phone_number'],
        )
        return user
