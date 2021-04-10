from rest_framework import serializers
from wallets.models import Wallet
from wallets.validators import deposit_is_valid


class WalletEmptySerializer(serializers.ModelSerializer):

    """
        WalletEmpty serializer is used for request which doesn't need to specify any field, like wallet creation
    """

    class Meta:
        model = Wallet
        fields = ()


class WalletDepositSerializer(serializers.ModelSerializer):

    """
        WalletDeposit serializer is used for request to deposit some money in a wallet
    """

    wallet = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, validators=[deposit_is_valid, ])

    class Meta:
        model = Wallet
        fields = ('wallet', 'amount',)


class WalletChargeSerializer(serializers.ModelSerializer):

    """
        WalletCharge serializer is used for request to make a charge to a client wallet
    """

    wallet = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, validators=[deposit_is_valid, ])
    summary = serializers.CharField(max_length=70)

    class Meta:
        model = Wallet
        fields = ('wallet', 'amount', 'summary')
