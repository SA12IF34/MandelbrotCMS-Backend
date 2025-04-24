from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
import uuid
from .managers import AccountManager


def upload_pic(self, filename):
    return f'accounts/pics/{self.id}/{filename}'

# Create your models here.
class Account(AbstractUser):
    username = None
    first_name = None
    last_name = None
    username = models.CharField(max_length=300, null=False, blank=False)
    email = models.EmailField(_('email address'), null=False, blank=False, unique=True)
    picture = models.FileField(upload_to=upload_pic, null=True, blank=True)
    about = models.TextField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = AccountManager()

    def __str__(self):
        return f'{self.username} | {self.email} | {self.id}'


TYPE_CHOICES = [
    ('anime&manga', 'anime&manga'),
    ('game', 'game'),
    ('shows&movies', 'shows&movies'),
    ('other', 'other')
]

class AccountSettings(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='settings')
    redirect_home = models.BooleanField(default=True, verbose_name='Redirect to home page')
    intro_parts_nav = models.BooleanField(default=False, verbose_name='Intro parts navigation')
    default_entertainment_type = models.CharField(max_length=25, choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0], null=True)
    open_sidenav = models.BooleanField(default=False, verbose_name='Open sidenav')

    def __str__(self):
        return f'{self.account.username} | {self.account.email} | {self.account.id}'