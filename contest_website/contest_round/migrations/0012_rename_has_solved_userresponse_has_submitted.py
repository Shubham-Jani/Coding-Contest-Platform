# Generated by Django 4.2.4 on 2023-09-26 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest_round', '0011_userresponse_unique_user_response'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userresponse',
            old_name='has_solved',
            new_name='has_submitted',
        ),
    ]
