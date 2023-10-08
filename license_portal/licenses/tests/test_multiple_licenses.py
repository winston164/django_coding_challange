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

class TestManyLicencesNotification(TestCase):
    @freeze_time("2023-01-02 12:00:00") # this date was a monday
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
        lic1 = License.objects.create(
            client=client,
            package=Package.javascript_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=6),
        )
        lic2 = License.objects.create(
            client=client,
            package=Package.javascript_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=30),
        )
        lic3 = License.objects.create(
            client=client,
            package=Package.javascript_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=31*4),
        )
        lics = {lic1, lic2, lic3}
        url = "/license-ms/notify/"

        # Execute
        response = self.client.post(url)

        # Assert
        self.assertEqual(response.status_code, 200)

        self.assertEqual(NotifyRequest.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), 1)


        expected_licenses = [
            {
                "id": lic.id,
                "type": lic.get_license_type_display(),
                "package": lic.get_package_display(),
                "expiration_date": lic.expiration_datetime.strftime("%Y-%m-%d"),
            }
            for lic in lics
        ]
        licenses = response.data["notifications"][0].pop("expiring_licenses")

        expected_licenses.sort(key=lambda lic: lic["id"])
        licenses.sort(key=lambda lic: lic["id"])

        self.assertEqual(expected_licenses, licenses)

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

