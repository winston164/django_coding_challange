from django.contrib.auth.models import User
from django.core import mail as django_email
from django.test import TestCase
from freezegun import freeze_time
from licenses.models import Notification, NotifyRequest

from .utils import get_clients_for, get_email_body, get_expiring_licenses_for, parse_license_from


class TestManyClientsNotification(TestCase):
    @freeze_time("2023-01-02 12:00:00")  # this date was a monday
    def test_multiple_clients(self):
        """
        Many Notifications for many Clients
        """

        # Prepare
        user = User.objects.create_user(
            username="user",
            email="user@email.com",
            password="password",
        )
        clients = get_clients_for(user)

        lics = []

        for client in clients:
            licenses = get_expiring_licenses_for(client)
            lics.extend(licenses)

        url = "/license-ms/notify/"

        # Execute
        response = self.client.post(url)

        # Assert Status
        self.assertEqual(response.status_code, 200)

        # Assert DB
        self.assertEqual(NotifyRequest.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), len(clients))
        notifications = list(Notification.objects.all())

        # Assert Expired Licenses
        expected_licenses = [parse_license_from(lic) for lic in lics]
        licenses = []
        for notification in response.data["notifications"]:
            lics = notification.pop("expiring_licenses")
            licenses.extend(lics)

        expected_licenses.sort(key=lambda lic: lic["id"])
        licenses.sort(key=lambda lic: lic["id"])

        self.assertEqual(expected_licenses, licenses)

        # Assert Response
        self.assertEqual(
            response.data,
            {
                "request_datetime": "2023-01-02T12:00:00Z",
                "notifications": [
                    {
                        "topic": "Expiration Warning",
                        "send_datetime": "2023-01-02T12:00:00Z",
                        "message": "",
                        "client_info": str(client),
                        "admin_name": "user",
                    }
                    for client in clients
                ],
            },
        )

        # Assert emails
        self.assertEqual(len(django_email.outbox), len(notifications))
        sent_emails = django_email.outbox
        sent_emails.sort(key=lambda email: email.to)
        notifications.sort(key=lambda notification: notification.user.email)

        for sent_email, notification in zip(sent_emails, notifications):

            expected_email_body = get_email_body(
                topic=notification.get_topic_display(),
                username=user.username,
                client=notification.client,
                licenses=notification.licenses.all(),
            )

            self.assertEqual(sent_email.subject, notification.get_topic_display())

            self.assertEqual(sent_email.from_email, "noreply@email.com")
            self.assertEqual(sent_email.to, [user.email])

            body = sent_email.body.splitlines()
            expected_body = expected_email_body.splitlines()

            self.assertEqual(len(body), len(expected_body))
            self.assertListEqual(body, expected_body)

