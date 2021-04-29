from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from wallets.models import Wallet
from users.models import User


class CompanyWalletTests(APITestCase):

    """
        Test cases for the wallet operations done by companies
    """

    def setUp(self):
        """ Configuring the data needed for the tests """
        self.client = APIClient()
        self.company_login_data = {
            'email': "test@company.com",
            'password': "Myt3xtP!"
        }
        self.company_user = User.objects.create_company(email=self.company_login_data['email'],
                                                        password=self.company_login_data['password'])
        self.company_token = "Token " + Token.objects.create(user=self.company_user).key
        self.company_wallet = Wallet.objects.create_new(self.company_user)

    def test_create_wallet(self):
        """ Ensure company can create a new wallet, and no more than one """
        company_user = User.objects.create_company(email="creation@company.com", password="Fo0PW!@")
        company_token = "Token " + Token.objects.create(user=company_user).key
        url = reverse('wallets:wallet_creation')
        response = self.client.post(url, {}, format='json', HTTP_AUTHORIZATION=company_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Wallet.objects.count_by_user(self.company_user), 1)
        # Try a new one, it must be not allowed
        response = self.client.post(url, {}, format='json', HTTP_AUTHORIZATION=company_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Wallet.objects.count_by_user(self.company_user), 1)

    def test_make_a_charge(self):
        """ Ensure companies can make charges to clients """
        client_user = User.objects.create_client(email="creation@client.com", password="Fo0PW2!@")
        client_wallet = Wallet.objects.create_new(client_user)
        client_wallet.deposit(10)
        url = reverse('wallets:wallet_charge')
        charge_data = {
            'wallet': client_wallet.token,
            'amount': 5,
            'summary': "Its a test charge!"
        }
        response = self.client.post(url, charge_data, format='json', HTTP_AUTHORIZATION=self.company_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.company_wallet.refresh_from_db()
        self.assertEqual(self.company_wallet.balance, 5)
        client_wallet.refresh_from_db()
        self.assertEqual(client_wallet.balance, 5)

    def test_list_wallet_history(self):
        """ Ensure companies can check his wallet history """
        url = reverse('wallets:wallet_history', kwargs={'wallet_token': self.company_wallet.token})
        response = self.client.get(url, {}, format='json', HTTP_AUTHORIZATION=self.company_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ClientWalletTests(APITestCase):

    """
        Test cases for the wallet operations done by clients
    """

    def setUp(self):
        """ Configuring the data needed for the tests """
        self.client = APIClient()
        self.client_login_data = {
            'email': "test@client.com",
            'password': "Myt3xtPW2!"
        }
        self.client_user = User.objects.create_company(email=self.client_login_data['email'],
                                                       password=self.client_login_data['password'])
        self.client_token = "Token " + Token.objects.create(user=self.client_user).key
        self.client_wallet = Wallet.objects.create_new(self.client_user)

    def test_create_many_wallets(self):
        """ Ensure client can create many wallets """
        client_user = User.objects.create_client(email="creation@client.com", password="Fo0PW2!@")
        client_token = "Token " + Token.objects.create(user=client_user).key
        url = reverse('wallets:wallet_creation')
        for number in range(1, 10):
            response = self.client.post(url, {}, format='json', HTTP_AUTHORIZATION=client_token)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Wallet.objects.count_by_user(client_user), number)

    def test_make_a_deposit(self):
        """ Ensure client can make a deposit in one of his wallet """
        url = reverse('wallets:wallet_deposit')
        deposit_data = {
            'wallet': self.client_wallet.token,
            'amount': 5
        }
        response = self.client.post(url, deposit_data, format='json', HTTP_AUTHORIZATION=self.client_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client_wallet.refresh_from_db()
        self.assertEqual(self.client_wallet.balance, 5)

    def test_get_wallets_info(self):
        """ Ensure client can check all his wallet information """
        url = reverse('wallets:wallet_list')
        response = self.client.get(url, {}, format='json', HTTP_AUTHORIZATION=self.client_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertTrue(response.data[0]['wallet'] == str(self.client_wallet.token))

    def test_list_wallet_history(self):
        """ Ensure client can check the history for a specific wallet """
        url = reverse('wallets:wallet_history', kwargs={'wallet_token': self.client_wallet.token})
        response = self.client.get(url, {}, format='json', HTTP_AUTHORIZATION=self.client_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
