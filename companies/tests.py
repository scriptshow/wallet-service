from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from companies.models import Company
from users.models import User


class CompaniesTests(APITestCase):

    """
        Test cases for the companies registration, login and logout
    """

    def setUp(self):
        """ Configuring the data needed for the tests """
        self.client = APIClient()
        self.company_creation_data = {
            'email': "test@test.com",
            'password': "srf82rn@!",
            'company': {
                'first_name': "Testing",
                'last_name': "User",
                'phone_number': "+34665069800",
                'name': "My Fake Company SL",
                'url': "https://www.myfakecompany.com/"
            }
        }
        self.company_login_data = {
            'email': "test@company.com",
            'password': "Myt3xtP!"
        }
        self.company_user = User.objects.create_company(email=self.company_login_data['email'],
                                                        password=self.company_login_data['password'])
        self.token = "Token " + Token.objects.create(user=self.company_user).key

    def test_create_company(self):
        """ Ensure we can create a new company """
        url = reverse('companies:company_signup')
        response = self.client.post(url, self.company_creation_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Company.objects.count(), 1)
        self.assertEqual(Company.objects.get().user.email, self.company_creation_data["email"])

    def test_login_company(self):
        """ Ensure we can login with a company """
        url = reverse('companies:company_login')
        response = self.client.post(url, self.company_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_logout_company(self):
        """ Ensure we can logout with a company """
        url = reverse('companies:company_logout')
        response = self.client.post(url, {}, format='json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
