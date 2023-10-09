from django.contrib.auth.models import User
from django.core import mail as django_email
from django.test import TestCase
from freezegun import freeze_time
from licenses.models import Client, Notification, NotifyRequest
from licenses.tests.utils import get_email_body, get_expiring_licenses_for, parse_license_from


class TestManyLicencesNotification(TestCase):
    @freeze_time("2023-01-02 12:00:00")  # this date was a monday
    def test_multiple_licenses(self):
        """
        Notification can handle many license warnings
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
        lics = get_expiring_licenses_for(client)

        url = "/license-ms/notify/"

        # Execute
        response = self.client.post(url)

        # Assert Status
        self.assertEqual(response.status_code, 200)

        # Assert DB
        self.assertEqual(NotifyRequest.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.get()

        # Assert Expired Licenses
        expected_licenses = [parse_license_from(lic) for lic in lics]
        licenses = response.data["notifications"][0].pop("expiring_licenses")
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
                ],
            },
        )

        # Assert email
        self.assertEqual(len(django_email.outbox), 1)
        sent_email = django_email.outbox[0]

        expected_email_body = get_email_body(
            topic=notification.get_topic_display(),
            username=user.username,
            client=client,
            licenses=lics,
        )

        self.assertEqual(sent_email.subject, notification.get_topic_display())

        self.assertEqual(sent_email.from_email, "noreply@email.com")
        self.assertEqual(sent_email.to, [user.email])

        body = sent_email.body.splitlines()
        expected_body = expected_email_body.splitlines()

        self.assertEqual(len(body), len(expected_body))
        self.assertListEqual(body, expected_body)

