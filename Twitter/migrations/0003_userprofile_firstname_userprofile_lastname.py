# Generated by Django 5.1.4 on 2024-12-16 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Twitter', '0002_userprofile_bio_userprofile_status_userprofile_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='firstname',
            field=models.CharField(blank=True, default='...', max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='lastname',
            field=models.CharField(blank=True, default='بی نام', max_length=120, null=True),
        ),
    ]