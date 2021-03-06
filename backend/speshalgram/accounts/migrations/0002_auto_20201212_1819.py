# Generated by Django 3.1.4 on 2020-12-11 15:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import speshalgram.accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('a', 'Accepted'), ('p', 'Pending'), ('r', 'Rejected')], max_length=1)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_follows_to', to=settings.AUTH_USER_MODEL)),
                ('follows_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub_followers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(fields=('follower', 'follows_to'), name='unique_subscription'),
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', speshalgram.accounts.models.CustomUserManager()),
            ],
        ),
    ]
