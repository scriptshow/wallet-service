from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.authentication import ExpiringTokenAuthentication
from wallets.serializers import WalletDepositSerializer, WalletChargeSerializer, WalletEmptySerializer
from wallets.models import Wallet, History
from companies.permissions import IsCompany


class WalletCreation(CreateAPIView):

    """
        WalletCreation is a class used as API endpoint to create new wallets
    """

    http_method_names = ['post']
    serializer_class = WalletEmptySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        user = request.user
        status_code = status.HTTP_201_CREATED
        response = {
            'success': 'True',
            'message': 'Wallet has been created successfully',
        }

        if Wallet.objects.can_create_new(user):
            wallet = Wallet.objects.create_new(user=user)
            response['wallet'] = wallet.token
        else:
            status_code = status.HTTP_403_FORBIDDEN
            response['success'] = 'False'
            response['message'] = 'Max limit of wallet created reached'

        response['status_code'] = status_code

        return Response(response, status=status_code)


class WalletList(CreateAPIView):

    """
        WalletList is a class used as API endpoint to list all the wallets for the authenticated user
    """

    http_method_names = ['get']
    serializer_class = WalletEmptySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def get(self, request):
        user = request.user
        status_code = status.HTTP_200_OK
        response = {
            'success': 'True',
            'message': 'Wallets have been found',
        }

        wallets = Wallet.objects.get_all_by_user(user)
        response['wallets'] = []
        for wallet in wallets:
            response['wallets'].append(wallet.to_json())

        response['status_code'] = status_code

        return Response(response, status=status_code)


class WalletInformation(CreateAPIView):

    """
        WalletInformation is a class used as API endpoint to view the information for specific wallet
    """

    http_method_names = ['get']
    serializer_class = WalletEmptySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def get(self, request, wallet_token=None):
        user = request.user
        status_code = status.HTTP_200_OK
        response = {
            'success': 'True',
            'message': 'Wallet has been found',
        }

        if wallet_token:
            wallet = Wallet.objects.get_by_token(wallet_token)
            if wallet:
                if wallet.check_if_owner(user):
                    response['wallet'] = wallet.to_json()
                else:
                    status_code = status.HTTP_403_FORBIDDEN
                    response['success'] = 'False'
                    response['message'] = 'You has not permissions for this wallet'
            else:
                status_code = status.HTTP_404_NOT_FOUND
                response['success'] = 'False'
                response['message'] = 'Wallet has not been found'
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response['success'] = 'False'
            response['message'] = 'Wallet is not valid'

        response['status_code'] = status_code

        return Response(response, status=status_code)


class WalletDeposit(CreateAPIView):

    """
        WalletDeposit is a class used as API endpoint to make a deposit in a wallet
    """

    http_method_names = ['post']
    serializer_class = WalletDepositSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        user = request.user
        status_code = status.HTTP_200_OK
        response = {
            'success': 'True',
            'message': 'Deposit has been done',
        }

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet_token = request.data['wallet']
        deposit_amount = request.data['amount']
        wallet = Wallet.objects.get_by_token(wallet_token)
        if wallet:
            if wallet.check_if_owner(user):
                wallet.deposit(deposit_amount)
                response['wallet'] = wallet.to_json()
            else:
                status_code = status.HTTP_403_FORBIDDEN
                response['success'] = 'False'
                response['message'] = 'You has not permissions for this wallet'
        else:
            status_code = status.HTTP_404_NOT_FOUND
            response['success'] = 'False'
            response['message'] = 'Wallet has not been found'

        response['status_code'] = status_code

        return Response(response, status=status_code)


class WalletHistory(CreateAPIView):

    """
        WalletHistory is a class used as API endpoint to list all the history data for a wallet
    """

    http_method_names = ['get']
    serializer_class = WalletEmptySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def get(self, request, wallet_token=None):
        user = request.user
        status_code = status.HTTP_200_OK
        response = {
            'success': 'True',
            'message': 'History has been found',
        }

        if wallet_token:
            wallet = Wallet.objects.get_by_token(wallet_token)
            if wallet:
                if wallet.check_if_owner(user):
                    histories = History.objects.get_full_history(wallet)
                    response['histories'] = [history.to_json() for history in histories]
                else:
                    status_code = status.HTTP_403_FORBIDDEN
                    response['success'] = False
                    response['message'] = 'You has not permissions for this wallet'
            else:
                status_code = status.HTTP_404_NOT_FOUND
                response['success'] = 'False'
                response['message'] = 'Wallet has not been found'
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response['success'] = 'False'
            response['message'] = 'Wallet is not valid'

        response['status_code'] = status_code

        return Response(response, status=status_code)


class WalletCharge(CreateAPIView):

    """
        WalletCharge is a class used as API endpoint to make charges from companies to clients
    """

    http_method_names = ['post']
    serializer_class = WalletChargeSerializer
    permission_classes = (IsAuthenticated, IsCompany,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        user = request.user
        status_code = status.HTTP_200_OK
        response = {
            'success': 'True',
            'message': 'Charge has been done',
        }

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet_token = request.data['wallet']
        deposit_amount = request.data['amount']
        summary = request.data['summary']
        target_wallet = Wallet.objects.get_unique_by_user(user)
        if target_wallet:
            try:
                if target_wallet.make_charge(wallet_token, deposit_amount, summary):
                    response['data'] = target_wallet.to_json()
                else:
                    status_code = status.HTTP_403_FORBIDDEN
                    response['success'] = False
                    response['message'] = 'Insufficient funds'
            except Wallet.DoesNotExist:
                status_code = status.HTTP_404_NOT_FOUND
                response['success'] = 'False'
                response['message'] = 'Wallet has not been found'
        else:
            status_code = status.HTTP_403_FORBIDDEN
            response['success'] = 'False'
            response['message'] = 'You need to create a wallet first'

        response['status_code'] = status_code

        return Response(response, status=status_code)
