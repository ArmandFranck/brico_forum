# Generated by Django 3.2.25 on 2024-11-03 22:51

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0003_auto_20241103_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='.posts/'),
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('follower', 'followed')},
        ),
    ]