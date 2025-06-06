# Generated by Django 5.1.4 on 2025-01-18 04:33

import entertainment.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entertainment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('description', models.TextField()),
                ('create_date', models.DateField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('user', models.PositiveIntegerField()),
                ('link', models.TextField()),
                ('type', models.CharField(choices=[('anime&manga', 'anime&manga'), ('game', 'game'), ('shows&movies', 'shows&movies'), ('other', 'other')], max_length=15)),
                ('subtype', models.CharField(choices=[('anime', 'anime'), ('manga', 'manga'), ('movie', 'movie'), ('show', 'show'), ('game', 'game')], default=None, max_length=10, null=True)),
                ('status', models.CharField(choices=[('current', 'current'), ('done', 'done'), ('future', 'future')], default=('current', 'current'), max_length=10)),
                ('special', models.BooleanField(default=False)),
                ('image', models.TextField(null=True)),
                ('image_upload', models.ImageField(default=None, null=True, upload_to=entertainment.models.upload_img)),
                ('rate', models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], default=None, null=True)),
                ('user_rate', models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], default=None, null=True)),
                ('locked', models.BooleanField(default=False)),
                ('lock_reason', models.IntegerField(default=None, null=True)),
                ('relatives', models.ManyToManyField(to='entertainment.entertainment')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
