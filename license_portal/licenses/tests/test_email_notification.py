from django.contrib.auth.models import User
from django.core import mail as django_email
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from licenses.models import (
    Client,
    License,
    LicenseType,
    Notification,
    NotificationTopic,
    Package,
)
from licenses.notifications import EmailNotification
from licenses.tests.utils import get_email_body


class TestEmailNotification(TestCase):
    @freeze_time("2023-01-01 12:00:00")
    def test_email_notifcation(self):
        """
        Email notification parse
        """

        # Prepare
        user = User.objects.create_user(
            username="user",
            email="user@email.com",
            password="password",
        )
        client = Client.objects.create(
            client_name="client",
            poc_contact_name="Client Example",
            poc_contact_email="client@email.com",
            admin_poc=user,
        )
        lic1 = License.objects.create(
            client=client,
            package=Package.javascript_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=6),
        )
        lic2 = License.objects.create(
            client=client,
            package=Package.ios_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=6),
        )
        lic3 = License.objects.create(
            client=client,
            package=Package.android_sdk,
            license_type=LicenseType.evaluation,
            expiration_datetime=timezone.now() + timezone.timedelta(days=6),
        )
        notification = Notification.objects.create(
            topic=NotificationTopic.expiration_warning,
            client=client,
            message="",
            user=user,
        )
        notification.licenses.set([lic1, lic2, lic3])
        notification.save()
        expected_email_body = get_email_body(
            topic=notification.get_topic_display(),
            username=user.username,
            client=client,
            licenses=[lic1, lic2, lic3],
        )

        # Execute
        EmailNotification.send_notification(notification, user.email)

        # Assert
        self.assertEqual(len(django_email.outbox), 1)

        sent_email = django_email.outbox[0]
        self.assertEqual(sent_email.subject, notification.get_topic_display())

        self.assertEqual(sent_email.from_email, "noreply@email.com")
        self.assertEqual(sent_email.to, [user.email])

        body = sent_email.body.splitlines()
        expected_body = expected_email_body.splitlines()

        self.assertEqual(len(body), len(expected_body))
        self.assertListEqual(body, expected_body)
