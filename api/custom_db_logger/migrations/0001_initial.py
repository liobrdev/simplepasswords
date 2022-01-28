# Generated by Django 3.2.9 on 2022-01-28 01:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='StatusLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asc_time', models.CharField(max_length=255)),
                ('client_ip', models.GenericIPAddressField(db_index=True, null=True)),
                ('command', models.CharField(db_index=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('filename', models.CharField(max_length=255)),
                ('func_name', models.CharField(max_length=255)),
                ('level', models.PositiveSmallIntegerField(choices=[(0, 'Notset'), (10, 'Debug'), (20, 'Info'), (30, 'Warning'), (40, 'Error'), (50, 'Critical')], db_index=True, default=40)),
                ('line_no', models.PositiveSmallIntegerField()),
                ('logger_name', models.CharField(db_index=True, max_length=255)),
                ('metadata', models.JSONField(null=True)),
                ('module', models.CharField(max_length=255)),
                ('msg', models.TextField()),
                ('pathname', models.CharField(max_length=500)),
                ('process', models.PositiveSmallIntegerField()),
                ('process_name', models.CharField(max_length=255)),
                ('thread', models.PositiveBigIntegerField()),
                ('thread_name', models.CharField(max_length=255)),
                ('trace', models.TextField(blank=True, null=True)),
                ('user', models.CharField(db_index=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Logging',
                'verbose_name_plural': 'Logging',
                'ordering': ('-created_at',),
            },
        ),
    ]
