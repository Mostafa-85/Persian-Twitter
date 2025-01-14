# Generated by Django 5.1.4 on 2024-12-30 18:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Twitter', '0012_post_post_picture_view_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='view_posts', to='Twitter.userprofile')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='Twitter.post')),
            ],
            options={
                'unique_together': {('from_user', 'post')},
            },
        ),
        migrations.DeleteModel(
            name='view_post',
        ),
    ]
