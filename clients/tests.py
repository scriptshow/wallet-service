from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from clients.models import Client
from users.models import User


class ClientsTests(APITestCase):

    """
        Test cases for the clients registration, login and logout
    """

    def setUp(self):
        """ Configuring the data needed for the tests """
        self.client = APIClient()
        self.client_creation_data = {
            'email': "test@test.com",
            'password': "srf82rn@!",
            'client': {
                'first_name': "Testing",
                'last_name': "User",
                'phone_number': "+34665069800"
            }
        }
        self.client_login_data = {
            'email': "test@company.com",
            'password': "Cl!3nTPW",
        }
        self.client_user = User.objects.create_client(email=self.client_login_data['email'],
                                                      password=self.client_login_data['password'])
        self.token = "Token " + Token.objects.create(user=self.client_user).key

    def test_create_client(self):
        """ Ensure we can create a new client """
        url = reverse('clients:client_signup')
        response = self.client.post(url, self.client_creation_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Client.objects.count(), 1)
        self.assertEqual(Client.objects.get().user.email, self.client_creation_data["email"])

    def test_login_client(self):
        """ Ensure we can login with a client """
        self.test_create_client()
        url = reverse('clients:client_login')
        response = self.client.post(url, self.client_login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.token = 'Token ' + response.data['token']

    def test_logout_client(self):
        """ Ensure we can logout with a client """
        self.test_login_client()
        url = reverse('clients:client_logout')
        response = self.client.post(url, {}, format='json', HTTP_AUTHORIZATION=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
