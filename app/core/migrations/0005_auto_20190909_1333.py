# Generated by Django 2.1.11 on 2019-09-09 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20190909_0233'),
    ]

    operations = [
        migrations.RenameField(
            model_name='description',
            old_name='userText',
            new_name='name',
        ),
    ]