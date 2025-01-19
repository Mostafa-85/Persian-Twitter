# Generated by Django 5.1.4 on 2025-01-01 19:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Twitter', '0015_followrequest_notifications_delete_followrequestw_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='followrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='followrequest',
            name='from_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_follow_requests', to='Twitter.userprofile'),
        ),
        migrations.AlterField(
            model_name='followrequest',
            name='to_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_follow_requests', to='Twitter.userprofile'),
        ),
    ]
