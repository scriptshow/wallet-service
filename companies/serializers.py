from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from companies.models import Company
from users.models import User


class CompanySerializer(serializers.ModelSerializer):

    """
        Default Company serializer
    """

    class Meta:
        model = Company
        fields = ('first_name', 'last_name', 'phone_number', 'name', 'url')


class CompanyRegistrationSerializer(serializers.ModelSerializer):

    """
        Serializer used to Sign up as Company
    """

    company = CompanySerializer(required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'company')
        extra_kwargs = {'password': {'write_only': True, 'validators': [validate_password, ]}}

    def create(self, validated_data):
        company_data = validated_data.pop('company')
        user = User.objects.create_company(**validated_data)
        Company.objects.create(
            user=user,
            first_name=company_data['first_name'],
            last_name=company_data['last_name'],
            phone_number=company_data['phone_number'],
            name=company_data['name'],
            url=company_data['url']
        )
        return user
