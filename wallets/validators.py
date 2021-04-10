from rest_framework import serializers
from decimal import Decimal, InvalidOperation


def deposit_is_valid(deposit):

    """
        Validator for the amount to be deposit or transfer to a wallet
        :param deposit: must be a numeric number, higher than 0
        :return: The number in Decimal format, if valid
    """

    try:
        decimal = Decimal(deposit)
        if decimal.is_signed() or decimal.is_zero():
            raise serializers.ValidationError("Amount to deposit must not be less or equals to 0")
        else:
            return decimal
    except InvalidOperation:
        raise serializers.ValidationError("Amount to deposit must be a number higher than 0")
