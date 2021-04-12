import uuid
from django.utils import timezone
from django.db import models, transaction
from users.models import User
from walletservice.settings import MAX_WALLETS_BY_COMPANY, MAX_WALLETS_BY_CLIENT
from django.core.exceptions import ValidationError


class WalletManager(models.Manager):

    """
        Wallet manager class will override the default manager adding extra functionalities for Wallet model.
    """

    def count_by_user(self, user):
        """ Return the number of wallets found for the user """
        return Wallet.objects.filter(user=user).count()

    def create_new(self, user):
        """ Return the wallet created """
        return Wallet.objects.create(user=user)

    def get_by_token(self, token):
        """ Return the wallet found, if not found return None """
        try:
            return Wallet.objects.get(token=token)
        except Wallet.DoesNotExist:
            return None
        except ValidationError:
            return None

    def can_create_new(self, user):
        """ Return True if can create new wallets, False if not """
        result = False
        if user.is_client:
            if MAX_WALLETS_BY_CLIENT == 0 or self.count_by_user(user) < MAX_WALLETS_BY_CLIENT:
                result = True
        elif user.is_company:
            if MAX_WALLETS_BY_COMPANY == 0 or self.count_by_user(user) < MAX_WALLETS_BY_COMPANY:
                result = True
        return result

    def get_all_by_user(self, user):
        """ Return a list of wallets for this user, empty list if no wallets found """
        return Wallet.objects.filter(user=user).all()

    def get_unique_by_user(self, user):
        """ Return a wallet if only one is created for this user, if many or not found, returning None """
        try:
            return Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            return None
        except Wallet.MultipleObjectsReturned:
            return None


class Wallet(models.Model):

    """
        Wallet model, used to store money.
        Identified by the UUID standards to manage transactions (deposits and charges).
    """

    # Using UUID standards to autogenerate the tokens which identifies each of the wallets.
    # https://www.mysqltutorial.org/mysql-uuid/
    # https://es.wikipedia.org/wiki/Identificador_%C3%BAnico_universal
    # https://en.wikipedia.org/wiki/Universally_unique_identifier#Collisions
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Taking into account that the richest companies manage around 100-200 Billions dollars,
    # let's dream about that these companies could be our customers, and in the future this amount can reach the
    # Trillion of dollars, setting the limit up to 12 digits.
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    # Using ForeignKey due we allow users to manage many wallets
    user = models.ForeignKey(User, related_name="wallet_user", null=False, blank=False, on_delete=models.PROTECT)

    # Overriding the default manager for our custom manager
    objects = WalletManager()

    class Meta:
        """ to set table name in database """
        db_table = "wallet"

    def __str__(self):
        return '{0} - {1}'.format(self.token, self.user.email)

    def to_json(self):
        """ Return the wallet information ready for json format """
        return {'wallet': self.token, 'balance': self.balance}

    def check_if_owner(self, user):
        """ Return True if the user is the owner of this wallet, False if not """
        return self.user == user

    def is_the_same(self, token):
        """ Return True if token belong to this wallet, False if not """
        return self.token == uuid.UUID(token)

    def deposit(self, amount):
        """ Make a deposit of money into the wallet """
        # Setting this transaction as atomic to easy rollback if something goes wrong
        with transaction.atomic():
            # Using the model F to protect against race condition
            # https://docs.djangoproject.com/en/1.8/ref/models/expressions/#django.db.models.F
            self.balance = models.F('balance') + amount
            self.save()
            # Storing the operation in the history
            History.objects.new_deposit(self, amount)
            # Refreshing from db to update the value after the deposit done
            self.refresh_from_db()

    def make_charge(self, source_wallet, amount, summary):
        """ Make a charge, taking the money from the wallet specified """
        # Setting this transaction as atomic to easy rollback if something goes wrong, additionally all the
        # activity done inside the atomic transaction will block the row used until finished
        with transaction.atomic():
            # Using select_for_update to block the row until the transaction is finished, it's needed in some
            # databases although transaction.atomic is enabled
            source_instance = Wallet.objects.select_for_update().get(token=source_wallet)
            if source_instance.balance >= amount:
                source_instance.balance -= amount
                self.balance = models.F('balance') + amount
                source_instance.save()
                self.save()
                History.objects.new_transfer(source_instance, self, summary, amount, True)
                # Refresing from db to update the value after the deposit done
                self.refresh_from_db()
                return True
            else:
                History.objects.new_transfer(source_instance, self, summary, amount, False)
                return False


class HistoryManager(models.Manager):

    """
        History manager class will override the default manager adding extra functionalities for History model.
    """

    def new_deposit(self, wallet, amount):
        """ Store into history the deposit transaction """
        History.objects.create(summary="Deposit", target=wallet, amount=amount)

    def new_transfer(self, source_wallet, target_wallet, summary, amount, success):
        """ Store into history the transfer transaction """
        History.objects.create(summary=summary, source=source_wallet, target=target_wallet, amount=amount,
                               success=success)

    def get_full_history(self, wallet):
        """ Return a list of history instances related with the wallet specified, ordered from newer to older """
        # Adding .values() function to do not query each one of the relations with the wallets, and do retrieve
        # all information with only one query
        return History.objects\
                      .filter(models.Q(source=wallet) | models.Q(target=wallet))\
                      .order_by('-date')\
                      .values('summary', 'source__token', 'target__token', 'amount', 'date', 'success')\
                      .all()


class History(models.Model):

    """
        History model, used to store all the transactions done in wallets.
    """

    # Short description about the transaction
    summary = models.CharField(max_length=70, blank=False, null=False)
    # Wallet where the money is get, it could be null if its just a deposit transaction
    source = models.ForeignKey(Wallet, related_name="wallet_source", null=True, blank=False, on_delete=models.CASCADE)
    # Wallet where the money is deposit
    target = models.ForeignKey(Wallet, related_name="wallet_target", null=False, blank=False, on_delete=models.CASCADE)

    # Max charge limit will be 999.999,00 maybe it's too much, but our clients could be very rich!
    # We are one of the best companies, and we will offer the limit our clients deserve
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)

    # The datetime where the transaction was done, it's automatically set when stored
    # Let's add an index for this field, maybe in the future, if we have a lot of transactions, we will need
    # to look for a transactions from a timeframe, and it will help in the speed of these queries
    date = models.DateTimeField(null=False, blank=False, default=timezone.now, db_index=True)

    # We are storing as boolean the result of this transaction, maybe a better approach could be to have a separate
    # field to store the result code, where we could specify the cause
    success = models.BooleanField(null=False, blank=False, default=True)

    objects = HistoryManager()

    class Meta:
        """ to set table name in database """
        db_table = "history"

    def __str__(self):
        return '[{0}] {1} - {2} € - ({3}) to ({4})'.format(self.success, self.summary, self.amount, self.source, self.target)

    def to_json(self):
        """ Return the history information ready for json format """
        if self.source:
            source = self.source.token
        else:
            source = None
        return {'summary': self.summary, 'source': source, 'target': self.target.token, 'amount': self.amount,
                'success': self.success, 'date': self.date}
