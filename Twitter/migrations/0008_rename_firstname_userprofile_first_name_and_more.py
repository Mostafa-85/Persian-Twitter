# Generated by Django 5.1.4 on 2024-12-21 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Twitter', '0007_alter_userprofile_bio_alter_userprofile_firstname_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='firstname',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='lastname',
            new_name='last_name',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='profile_pics/nody-عکس-پروفایل-مخصوص-واتساپ-؛-؛-1717325475.jpg', upload_to='profile_pics/'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='status',
            field=models.BooleanField(choices=[(True, 'فعال'), (False, 'غیرفعال')], default=True),
        ),
    ]
