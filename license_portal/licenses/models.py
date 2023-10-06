""" Data model for licenses application
"""

from datetime import timedelta, datetime

from django.contrib.auth.models import User
from django.db import models

LICENSE_EXPIRATION_DELTA = timedelta(days=90)


class Package(models.IntegerChoices):
    """A Package accessible to a client with a valid license"""
    javascript_sdk = 0, "JavaScript SDK"
    ios_sdk = 1, "IOS SDK"
    android_sdk = 2, "Android SDK"


class LicenseType(models.IntegerChoices):
    """A license type"""
    production = 0, "Production"
    evaluation = 1, "Evaluation"


def get_default_license_expiration() -> datetime:
    """Get the default expiration datetime"""
    return datetime.utcnow() + LICENSE_EXPIRATION_DELTA


class License(models.Model):
    """ Data model for a client license allowing access to a package
    """
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    package = models.PositiveSmallIntegerField(choices=Package.choices)
    license_type = models.PositiveSmallIntegerField(choices=LicenseType.choices)

    created_datetime = models.DateTimeField(auto_now=True)
    expiration_datetime = models.DateTimeField(default=get_default_license_expiration)

    def __str__(self):
        expiration_date = self.expiration_datetime.strftime('%Y-%m-%d')
        return f"""
License: 
  id: {self.id if self.id else "not created yet"}
  license type: {self.get_license_type_display()}
  package: {self.get_package_display()}
  expiration date: {expiration_date}
  client: {self.client}
"""


class Client(models.Model):
    """ A client who holds licenses to packages
    """
    client_name = models.CharField(max_length=120, unique=True)
    poc_contact_name = models.CharField(max_length=120)
    poc_contact_email = models.EmailField()

    admin_poc = models.ForeignKey(User, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.poc_contact_name}, {self.poc_contact_email}"

class NotificationTopic(models.TextChoices):
    expiration_warning = 'Expiration Warning'

class Notification(models.Model):
    """ A Notification sent to a user
    """
    
    topic = models.CharField(max_length=120, choices=NotificationTopic.choices)
    send_datetime = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(Client, null=True, on_delete=models.SET_NULL)
    message = models.TextField()
    licenses = models.ManyToManyField(License)
    user = models.ForeignKey(User, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)

class NotifyRequestMedium(models.TextChoices):
    email = 'email'

class NotifyRequest(models.Model):
    
    # TODO: consider adding:
    # topics = models.ArrayField(
    #     models.CharField(max_length=120, choices=NotificationTopic.choices),
    # )
    # medium = models.CharField(max_length=120, choices=NotifyRequestMedium)
    # filter = models.JSONField(
    #     blank=True,
    #     ediatble=False,
    #     help_text=
    #     """
    #     JSON field to set notification request filters like:
    #     * Which clients
    #     * Which users
    #     * Which licenses
    #     """
    # )
    request_datetime = models.DateTimeField(auto_now=True)
    notifications = models.ManyToManyField(Notification, blank=True)


