from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time
from licenses.models import (Client, License, LicenseType, Notification,
                             NotifyRequest, Package)


class TestCreateNotification(TestCase):
    @freeze_time("2023-01-01 12:00:00")
    def test_week_expiration(self):
        """
        Test to verify a notification resource is created
        when a license expires in a week
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
        License.objects.create(
            client=client,
            package=Package.javascript_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=6),
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
                "request_datetime": "2023-01-01T12:00:00Z",
                "notifications": [
                    {
                        "topic": "Expiration Warning",
                        "send_datetime": "2023-01-01T12:00:00Z",
                        "message": "",
                        "client_info": str(client),
                        "admin_name": "user",
                        "expiring_licenses": [
                            {
                                "type": "Production",
                                "package": "JavaScript SDK",
                                "expiration_date": "2023-01-07",
                            }
                        ],
                    }
                ],
            },
        )
