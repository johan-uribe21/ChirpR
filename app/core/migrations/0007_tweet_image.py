# Generated by Django 2.1.12 on 2019-09-09 19:44

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_tweet'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.tweet_image_file_path),
        ),
    ]