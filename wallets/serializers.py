from rest_framework import serializers
from wallets.models import Wallet, History
from wallets.validators import deposit_is_valid


class WalletListSerializer(serializers.ListSerializer):

    """
        Wallet List serializer is used when listing multiple wallets
    """

    def output_data(self):
        return [{'wallet': data['token'], 'balance': data['balance']} for data in self.data]


class WalletSerializer(serializers.ModelSerializer):

    """
        Wallet serializer is used for generic wallet request, like wallet creation
    """

    class Meta:
        model = Wallet
        list_serializer_class = WalletListSerializer
        fields = '__all__'

    def create(self, validated_data):
        return Wallet.objects.create_new(user=validated_data['user'])

    def can_create_new(self):
        return Wallet.objects.can_create_new(self.validated_data['user'])

    def output_data(self):
        return {'wallet': self.data['token'], 'balance': self.data['balance']}


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


class HistorySerializer(serializers.ModelSerializer):

    """
        History serializer is used for generic history request
    """

    class Meta:
        model = History
        fields = '__all__'
