# Generated by Django 4.2.5 on 2023-09-13 07:19

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='bio',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(blank=True, default='accounts/users/default.svg', null=True, upload_to=accounts.models.user_media_directory),
        ),
    ]
