# Generated by Django 5.1.4 on 2025-02-16 06:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_tracker', '0002_alter_course_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='progress',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
