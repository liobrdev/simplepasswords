# Generated by Django 3.2.9 on 2022-01-28 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerificationToken',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('token_key', models.CharField(db_index=True, max_length=8)),
                ('salt', models.CharField(max_length=16, unique=True)),
                ('digest', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('expiry', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PhoneVerificationToken',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('salt', models.CharField(max_length=16, unique=True)),
                ('digest', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('expiry', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TwoFactorAuthToken',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('salt', models.CharField(max_length=16, unique=True)),
                ('digest', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('expiry', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
