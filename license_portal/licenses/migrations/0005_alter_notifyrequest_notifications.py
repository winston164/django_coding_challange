# Generated by Django 4.2.5 on 2023-10-02 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licenses', '0004_notification_notifyrequest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifyrequest',
            name='notifications',
            field=models.ManyToManyField(blank=True, to='licenses.notification'),
        ),
    ]
