from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from licenses.models import (
    Client,
    License,
    LicenseType,
    Notification,
    NotifyRequest,
    Package,
)
from licenses.tests.utils import parse_license_from


class TestMondayNotification(TestCase):
    @freeze_time("2023-01-02 12:00:00")  # this date was a monday
    def test_monday_warning(self):
        """
        Test to verify a notification resource is created
        when a license expires in a month and today is monday
        (assume one month = 31 days)
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
        lic = License.objects.create(
            client=client,
            package=Package.javascript_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=30),
        )
        url = "/license-ms/notify/"

        # Execute
        response = self.client.post(url)

        # Assert
        self.assertEqual(response.status_code, 200)

        self.assertEqual(NotifyRequest.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 1)

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
                        "admin_name": user.username,
                        "expiring_licenses": [parse_license_from(lic)],
                    }
                ],
            },
        )
