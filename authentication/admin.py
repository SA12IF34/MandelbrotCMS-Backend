from django.contrib import admin
from .models import Account, AccountSettings

admin.site.register(Account)
admin.site.register(AccountSettings)