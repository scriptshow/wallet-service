from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class UserManager(BaseUserManager):

    """
        Creating a manager for a custom user model
        https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model
        https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#a-full-example
    """

    def create_user(self, email, password=None):
        """
            Create and return a `User`, this user will not be client neither company, will be available only for
            superuser creation.
        """
        if not email:
            raise ValueError('Users Must Have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_client(self, email, password=None):
        """ Create and return a `User` as a client """
        if not email:
            raise ValueError('Users Must Have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.is_client = True
        user.save(using=self._db)
        return user

    def create_company(self, email, password=None):
        """ Create and return a `User` as a company """
        if not email:
            raise ValueError('Users Must Have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.is_company = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """ Create and return a `User` with superuser (admin) permissions """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):

    """
        Custom User model, it has been created to allow to store some information like if it's user created
        from a client or from a company. This user as well have been modified to delete the username, in modern
        applications the username is not needed unless the application itself need it, in our case, it's not
        needed and is easier to work only with email's as accounts.
    """

    id = models.AutoField(primary_key=True, editable=False)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
        )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Information added to store the role of the user
    is_client = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        '''
        to set table name in database
        '''
        db_table = "user"
