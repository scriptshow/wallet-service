from django.db import models
from users.models import User
from users.validators import phone_validator


class Company(models.Model):

    """
        Company model used to store the companies information
    """

    # 35 characters must be enough for any company name
    name = models.CharField(max_length=35)

    # The maximum of characters length for a domain is 63, including the rest of stuff which makes an url browsable
    # could go up to around 70 characters, so, let's think in our companies and care about them, if the largest
    # domain name company want to be in our system, let's make it possible!
    # Of course we are not taking into account the subdomains length (if yes it could go up to 253 characters), if
    # a company url doesnt fit in 70 characters... think about to use a url shortener.
    # https://en.wikipedia.org/wiki/Hostname#Syntax
    url = models.CharField(max_length=70)

    # Using the most common standard length, 35 for each one and a total of 70
    # Maybe our friend Wolfeschlegelsteinhausenbergerdorff can not fit all his names,
    # but with the short one is enough
    first_name = models.CharField(max_length=35, unique=False)
    last_name = models.CharField(max_length=35, unique=False)

    # Phone number will be unique per company, and will be validated
    phone_number = models.CharField(validators=[phone_validator, ], max_length=17, blank=False, null=False, unique=True)

    # It's a one to one field, because no more than one company by user is allowed
    user = models.OneToOneField(User, related_name="company_user", null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        """ to set table name in database """
        db_table = "company"

    def __str__(self):
        return '{0} - {1}'.format(self.name, self.user.email)
