# Generated by Django 5.1.4 on 2025-02-21 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entertainment', '0007_alter_entertainment_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='entertainment',
            name='release_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]
