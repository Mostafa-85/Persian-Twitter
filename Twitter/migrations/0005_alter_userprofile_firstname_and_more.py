# Generated by Django 5.1.4 on 2024-12-18 08:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Twitter', '0004_alter_userprofile_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='firstname',
            field=models.CharField(blank=True, default='', max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='lastname',
            field=models.CharField(blank=True, default='', max_length=120, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, default='profile_pics/nody-عکس-پروفایل-مخصوص-واتساپ-؛-؛-1717325475.jpg', null=True, upload_to='profile_pics/'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='status',
            field=models.BooleanField(choices=[(True, 'فعال'), (False, 'غیرفعال')], default=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='type',
            field=models.BooleanField(choices=[(True, 'خصوصی'), (False, 'عمومی')], default=False),
        ),
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to='Twitter.userprofile')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='Twitter.userprofile')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('from_user', 'to_user'), name='unique_following')],
            },
        ),
    ]
