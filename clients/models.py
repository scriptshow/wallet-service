from django.db import models
from users.models import User
from users.validators import phone_validator


class Client(models.Model):

    """
        Client model used to store the clients information
    """

    # Using the most common standard length, 35 for each one and a total of 70
    # Maybe our friend Wolfeschlegelsteinhausenbergerdorff can not fit all his names,
    # but with the short one is enough
    first_name = models.CharField(max_length=35, unique=False)
    last_name = models.CharField(max_length=35, unique=False)

    # Phone number will be unique per company, and will be validated
    phone_number = models.CharField(validators=[phone_validator, ], max_length=17, blank=False, null=False, unique=True)

    # It's a one to one field, because no more than one client by user is allowed
    user = models.OneToOneField(User, related_name="client_user", null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        """ to set table name in database """
        db_table = "client"

    def __str__(self):
        return '{0} {1} - {2}'.format(self.first_name, self.last_name, self.user.email)
