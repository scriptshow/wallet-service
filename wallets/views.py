from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.authentication import ExpiringTokenAuthentication
from wallets.serializers import WalletDepositSerializer, WalletChargeSerializer, WalletEmptySerializer
from wallets.models import Wallet, History
from users.permissions import IsCompany
from logging import getLogger

logger = getLogger(__name__)


class WalletCreation(CreateAPIView):

    """
        WalletCreation is a class used as API endpoint to create new wallets
    """

    http_method_names = ['post']
    serializer_class = WalletEmptySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        logger.info("User is requesting to create a new wallet")
        user = request.user
        status_code = status.HTTP_201_CREATED
        response = {
            'success': 'True',
            'message': "Wallet has been created successfully",
        }

        if Wallet.objects.can_create_new(user):
            logger.debug("User can create new wallets")
            wallet = Wallet.objects.create_new(user=user)
            response['wallet'] = wallet.token
            logger.info("Wallet has been created")
        else:
            status_code = status.HTTP_403_FORBIDDEN
            response['success'] = 'False'
            response['message'] = "Max limit of wallet created reached"
            logger.info("User can not create new wallets")

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
        logger.info("User is requesting the list of wallets assigned to him")
        user = request.user
        status_code = status.HTTP_200_OK
        response = {
            'success': 'True',
            'message': "Wallets have been found"
        }

        wallets = Wallet.objects.get_all_by_user(user)
        logger.debug("{0} wallets found for user".format(len(wallets)))
        response['wallets'] = []
        for wallet in wallets:
            response['wallets'].append(wallet.to_json())

        logger.info("Sending the list of wallets to user")
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
        logger.info("User is requesting information for wallet: {0}".format(wallet_token))
        user = request.user
        status_code = status.HTTP_200_OK
        response = {
            'success': 'True',
            'message': "Wallet has been found"
        }

        if wallet_token:
            wallet = Wallet.objects.get_by_token(wallet_token)
            if wallet:
                logger.debug("Wallet has been found")
                if wallet.check_if_owner(user):
                    logger.debug("User is the owner of this wallet")
                    response['wallet'] = wallet.to_json()
                    logger.info("Wallet information found, sending it to user")
                else:
                    logger.info("User is not the owner of this wallet")
                    status_code = status.HTTP_403_FORBIDDEN
                    response['success'] = 'False'
                    response['message'] = "You has not permissions for this wallet"
            else:
                logger.info("Wallet has not been found")
                status_code = status.HTTP_404_NOT_FOUND
                response['success'] = 'False'
                response['message'] = "Wallet has not been found"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response['success'] = 'False'
            response['message'] = "Wallet is not valid"

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
        logger.info("User is making a deposit in a wallet")
        user = request.user
        status_code = status.HTTP_200_OK
        response = {
            'success': 'True',
            'message': "Deposit has been done"
        }

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet_token = request.data['wallet']
        logger.debug("Wallet to be used: {0}".format(wallet_token))
        deposit_amount = request.data['amount']
        logger.debug("Amount to be deposit: {0}".format(deposit_amount))
        wallet = Wallet.objects.get_by_token(wallet_token)
        if wallet:
            logger.debug("Wallet has been found")
            if wallet.check_if_owner(user):
                logger.debug("User is the owner of this wallet")
                wallet.deposit(deposit_amount)
                logger.info("Deposit has been done")
                response['wallet'] = wallet.to_json()
            else:
                logger.info("User is not the owner of this wallet")
                status_code = status.HTTP_403_FORBIDDEN
                response['success'] = 'False'
                response['message'] = "You has not permissions for this wallet"
        else:
            logger.info("Wallet has not been found")
            status_code = status.HTTP_404_NOT_FOUND
            response['success'] = 'False'
            response['message'] = "Wallet has not been found"

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
        logger.info("User is requesting the operations history for wallet: {0}".format(wallet_token))
        user = request.user
        status_code = status.HTTP_200_OK
        response = {
            'success': 'True',
            'message': "History has been found"
        }

        if wallet_token:
            wallet = Wallet.objects.get_by_token(wallet_token)
            if wallet:
                logger.debug("Wallet has been found")
                if wallet.check_if_owner(user):
                    logger.debug("User is the owner of this wallet")
                    histories = History.objects.get_full_history(wallet)
                    logger.debug("{0} history operations have been found".format(len(histories)))
                    response['histories'] = histories
                    logger.info("Sending the operations histories to user")
                else:
                    logger.info("User is not the owner of this wallet")
                    status_code = status.HTTP_403_FORBIDDEN
                    response['success'] = False
                    response['message'] = "You has not permissions for this wallet"
            else:
                logger.info("Wallet has not been found")
                status_code = status.HTTP_404_NOT_FOUND
                response['success'] = 'False'
                response['message'] = "Wallet has not been found"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response['success'] = 'False'
            response['message'] = "Wallet is not valid"

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
        logger.info("Company is trying to make a charge to a client")
        user = request.user
        status_code = status.HTTP_200_OK
        response = {
            'success': 'True',
            'message': "Charge has been done"
        }

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet_token = request.data['wallet']
        logger.debug("Client wallet to be used: {0}".format(wallet_token))
        deposit_amount = request.data['amount']
        logger.debug("Amount to be charged: {0}".format(deposit_amount))
        summary = request.data['summary']
        logger.debug("Summary for this charge: {0}".format(summary))
        target_wallet = Wallet.objects.get_unique_by_user(user)
        if target_wallet:
            logger.debug("Company wallet to send the money: {0}".format(target_wallet.token))
            if not target_wallet.is_the_same(wallet_token):
                try:
                    if target_wallet.make_charge(wallet_token, deposit_amount, summary):
                        logger.info("Charge has been done")
                        response['wallet'] = target_wallet.to_json()
                    else:
                        logger.info("Charge couldn't be done, client has not funds")
                        status_code = status.HTTP_403_FORBIDDEN
                        response['success'] = False
                        response['message'] = "Insufficient funds"
                except Wallet.DoesNotExist:
                    logger.info("Client wallet does not exists")
                    status_code = status.HTTP_404_NOT_FOUND
                    response['success'] = 'False'
                    response['message'] = "Wallet has not been found"
            else:
                status_code = status.HTTP_403_FORBIDDEN
                response['success'] = False
                response['message'] = "You can not make a charge to yourself"
        else:
            logger.info("Company has not any wallet created, it's needed to make a charge")
            status_code = status.HTTP_403_FORBIDDEN
            response['success'] = 'False'
            response['message'] = "You need to create a wallet first"

        response['status_code'] = status_code

        return Response(response, status=status_code)
