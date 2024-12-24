# Generated by Django 5.1.4 on 2024-12-22 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Twitter', '0009_post_comment_like'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(max_length=250),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=50),
        ),
        migrations.AddField(
            model_name='post',
            name='hashtags',
            field=models.ManyToManyField(related_name='posts', to='Twitter.hashtag'),
        ),
    ]