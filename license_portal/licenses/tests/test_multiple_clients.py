from django.contrib.auth.models import User
from django.test import TestCase
from freezegun import freeze_time
from licenses.models import (
    Client,
    Notification,
    NotifyRequest,
)
from .utils import get_expiring_licenses_for

class TestManyClientsNotification(TestCase):
    @freeze_time("2023-01-02 12:00:00") # this date was a monday
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
        clients = [
            Client.objects.create(
                client_name=f"client{n}",
                poc_contact_name=f"Client{n} Example",
                poc_contact_email=f"client{n}@email.com",
                admin_poc=user,
            )
            for n in range(3)
        ]


        lics = []

        for client in clients:
            licenses = get_expiring_licenses_for(client)
            lics.extend(licenses)
        


        url = "/license-ms/notify/"

        # Execute
        response = self.client.post(url)

        # Assert
        self.assertEqual(response.status_code, 200)

        self.assertEqual(NotifyRequest.objects.count(), 1)
        self.assertEqual(Notification.objects.count(), len(clients))


        expected_licenses = [
            {
                "id": lic.id,
                "type": lic.get_license_type_display(),
                "package": lic.get_package_display(),
                "expiration_date": lic.expiration_datetime.strftime("%Y-%m-%d"),
            }
            for lic in lics
        ]
        licenses = []
        for notification in response.data["notifications"]:
            lics = notification.pop("expiring_licenses")
            licenses.extend(lics)

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
                    } for client in clients 
                ],
            },
        )


