from rest_framework import serializers
from .models import Account, AccountSettings

class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('username', 'email', 'picture', 'about')


class SettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountSettings
        fields = '__all__'