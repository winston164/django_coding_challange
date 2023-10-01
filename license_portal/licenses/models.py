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


class Client(models.Model):
    """ A client who holds licenses to packages
    """
    client_name = models.CharField(max_length=120, unique=True)
    poc_contact_name = models.CharField(max_length=120)
    poc_contact_email = models.EmailField()

    admin_poc = models.ForeignKey(User, limit_choices_to={'is_staff': True}, on_delete=models.CASCADE)
