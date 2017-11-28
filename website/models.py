from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


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

    def create_superuser(self, email, first_name, last_name, password, founder=False, **extra_fields):
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
        help_text='Must be a @berkeley.edu email',
        error_messages={'unique': 'A user with this email address already exists'}
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    registered_at = models.DateTimeField(auto_now_add=True, editable=False)
    first_name = models.CharField(verbose_name='First Name', max_length=25)
    last_name = models.CharField(verbose_name='Last Name', max_length=40)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    first_login = models.BooleanField(default=True)
    is_individual = models.BooleanField(default=False)
    is_founder = models.BooleanField(verbose_name='Is Founder', default=False)
    is_account_disabled = models.BooleanField(default=False)
    test_mode = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now, null=True)

    def set_first_login(self):
        if self.first_login:
            self.first_login = False
            self.save()

    def set_is_founder(self):
        if not self.is_founder:
            self.is_founder = True
            self.save()

    def set_is_individual(self):
        if not self.is_individual:
            self.is_individual = True
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

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def email_user(self, subject, message, from_email=None, html_content=None):
        if hasattr(settings, 'TEST_EMAIL'):
            to = [settings.TEST_EMAIL]
        else:
            to = [self.email]

        msg = EmailMultiAlternatives(subject, message, from_email, to)
        if not html_content is None:
            msg.attach_alternative(html_content, 'text/html')
        msg.send()

    def get_profile_url(self):
        try:
            return reverse('website:get_profile_view', kwargs={'id': self.profile.pk})
        except ObjectDoesNotExist as e:
            return None

    def get_startup_url(self):
        try:
            return reverse('website:get_startup_view', kwargs={'id': self.founder.pk})
        except ObjectDoesNotExist as e:
            return None

    def set_activity(self):
        if self.last_activity.date() != timezone.now().date():
            self.last_activity = timezone.now()
            self.save()

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
