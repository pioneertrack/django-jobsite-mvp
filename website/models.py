from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, first_name, last_name, founder, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_founder = founder
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, founder=False, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, first_name, last_name, founder, password, **extra_fields)

    def create_superuser(self, email, first_name, last_name, password, founder = False, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        return self._create_user(email, first_name, last_name, founder, password, **extra_fields)


class MyUser(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        help_text = 'Must be a @berkeley.edu email',
        error_messages = {'unique': 'A user with this email address already exists'}
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    first_name = models.CharField(verbose_name='First Name',max_length = 25)
    last_name = models.CharField(verbose_name='Last Name',max_length = 40)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    first_login = models.BooleanField(blank = True, default=True)
    is_individual = models.BooleanField(blank=True, default=True)
    is_founder = models.BooleanField(verbose_name='Is Founder',blank = True, default=False)

    def set_first_login(self):
        self.first_login = False
        self.save()

    def get_username(self):
        return self.email

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def get_is_founder(self):
        return self.is_founder

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
