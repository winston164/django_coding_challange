# Generated by Django 4.2.5 on 2023-10-02 03:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('licenses', '0003_alter_license_license_type_alter_license_package'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(choices=[('Expiration Warning', 'Expiration Warning')], max_length=120)),
                ('send_datetime', models.DateTimeField(auto_now=True)),
                ('message', models.TextField()),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='licenses.client')),
                ('licenses', models.ManyToManyField(to='licenses.license')),
                ('user', models.ForeignKey(limit_choices_to={'is_staff': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='NotifyRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_datetime', models.DateTimeField(auto_now=True)),
                ('notifications', models.ManyToManyField(to='licenses.notification')),
            ],
        ),
    ]
