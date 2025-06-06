# Generated by Django 5.1.4 on 2025-03-30 16:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_alter_account_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('redirect_home', models.BooleanField(default=True, verbose_name='Redirect to home page')),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
