from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.authentication import ExpiringTokenAuthentication
from wallets.serializers import WalletDepositSerializer, WalletChargeSerializer, WalletSerializer, HistorySerializer
from wallets.models import Wallet, History
from users.permissions import IsCompany
from logging import getLogger

logger = getLogger(__name__)


class WalletCreation(CreateAPIView):

    """
        WalletCreation is a class used as API endpoint to create new wallets
    """

    serializer_class = WalletSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        logger.info("User is requesting to create a new wallet")
        user = request.user

        serializer = self.serializer_class(data={'user': user.pk})
        serializer.is_valid(raise_exception=True)

        if serializer.can_create_new():
            logger.debug("User can create new wallets")
            serializer.save()
            logger.info("Wallet has been created")
            response = serializer.output_data()
            status_code = status.HTTP_201_CREATED
        else:
            response = "Max limit of wallet created reached"
            status_code = status.HTTP_403_FORBIDDEN

        return Response(response, status=status_code)


class WalletList(ListAPIView):

    """
        WalletList is a class used as API endpoint to list all the wallets for the authenticated user
    """

    serializer_class = WalletSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        logger.info("User is requesting the list of wallets assigned to him")
        user = request.user
        status_code = status.HTTP_200_OK

        wallets = Wallet.objects.get_all_by_user(user)
        serializer = self.serializer_class(wallets, many=True)
        logger.debug("{0} wallets found for user".format(len(wallets)))
        response = serializer.output_data()

        logger.info("Sending the list of wallets to user")

        return Response(response, status=status_code)


class WalletInformation(ListAPIView):

    """
        WalletInformation is a class used as API endpoint to view the information for specific wallet
    """

    serializer_class = WalletSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def get(self, request, wallet_token=None, *args, **kwargs):
        logger.info("User is requesting information for wallet: {0}".format(wallet_token))
        user = request.user
        status_code = status.HTTP_200_OK

        if wallet_token:
            wallet = Wallet.objects.get_by_token(wallet_token)
            if wallet:
                logger.debug("Wallet has been found")
                if wallet.check_if_owner(user):
                    logger.debug("User is the owner of this wallet")
                    serializer = self.serializer_class(wallet)
                    response = serializer.output_data()
                    logger.info("Wallet information found, sending it to user")
                else:
                    logger.info("User is not the owner of this wallet")
                    status_code = status.HTTP_403_FORBIDDEN
                    response = "You has not permissions for this wallet"
            else:
                logger.info("Wallet has not been found")
                status_code = status.HTTP_404_NOT_FOUND
                response = "Wallet has not been found"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = "Wallet is not valid"

        return Response(response, status=status_code)


class WalletDeposit(CreateAPIView):

    """
        WalletDeposit is a class used as API endpoint to make a deposit in a wallet
    """

    http_method_names = ['post']
    serializer_class = WalletDepositSerializer
    output_serializer_class = WalletSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        logger.info("User is making a deposit in a wallet")
        user = request.user
        status_code = status.HTTP_200_OK

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        wallet_token = serializer.data['wallet']
        logger.debug("Wallet to be used: {0}".format(wallet_token))
        deposit_amount = serializer.data['amount']
        logger.debug("Amount to be deposit: {0}".format(deposit_amount))
        wallet = Wallet.objects.get_by_token(wallet_token)
        if wallet:
            logger.debug("Wallet has been found")
            if wallet.check_if_owner(user):
                logger.debug("User is the owner of this wallet")
                wallet.deposit(deposit_amount)
                logger.info("Deposit has been done")
                serializer = self.output_serializer_class(wallet)
                response = serializer.output_data()
            else:
                logger.info("User is not the owner of this wallet")
                status_code = status.HTTP_403_FORBIDDEN
                response = "You has not permissions for this wallet"
        else:
            logger.info("Wallet has not been found")
            status_code = status.HTTP_404_NOT_FOUND
            response = "Wallet has not been found"

        return Response(response, status=status_code)


class WalletHistory(ListAPIView):

    """
        WalletHistory is a class used as API endpoint to list all the history data for a wallet
    """

    serializer_class = HistorySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def get(self, request, wallet_token=None, *args, **kwargs):
        logger.info("User is requesting the operations history for wallet: {0}".format(wallet_token))
        user = request.user
        status_code = status.HTTP_200_OK

        if wallet_token:
            wallet = Wallet.objects.get_by_token(wallet_token)
            if wallet:
                logger.debug("Wallet has been found")
                if wallet.check_if_owner(user):
                    logger.debug("User is the owner of this wallet")
                    histories = History.objects.get_full_history(wallet)
                    logger.debug("{0} history operations have been found".format(len(histories)))
                    response = histories
                    logger.info("Sending the operations histories to user")
                else:
                    logger.info("User is not the owner of this wallet")
                    status_code = status.HTTP_403_FORBIDDEN
                    response = "You has not permissions for this wallet"
            else:
                logger.info("Wallet has not been found")
                status_code = status.HTTP_404_NOT_FOUND
                response = "Wallet has not been found"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response = "Wallet is not valid"

        return Response(response, status=status_code)


class WalletCharge(CreateAPIView):

    """
        WalletCharge is a class used as API endpoint to make charges from companies to clients
    """

    serializer_class = WalletChargeSerializer
    output_serializer_class = WalletSerializer
    permission_classes = (IsAuthenticated, IsCompany,)
    authentication_classes = (ExpiringTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        logger.info("Company is trying to make a charge to a client")
        user = request.user
        status_code = status.HTTP_200_OK

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
                        serializer = self.output_serializer_class(target_wallet)
                        response = serializer.output_data()
                    else:
                        logger.info("Charge couldn't be done, client has not funds")
                        status_code = status.HTTP_403_FORBIDDEN
                        response = "Insufficient funds"
                except Wallet.DoesNotExist:
                    logger.info("Client wallet does not exists")
                    status_code = status.HTTP_404_NOT_FOUND
                    response = "Wallet has not been found"
            else:
                status_code = status.HTTP_403_FORBIDDEN
                response = "You can not make a charge to yourself"
        else:
            logger.info("Company has not any wallet created, it's needed to make a charge")
            status_code = status.HTTP_403_FORBIDDEN
            response = "You need to create a wallet first"

        return Response(response, status=status_code)
