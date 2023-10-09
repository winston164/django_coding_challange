from django.contrib.auth.models import User
from django.test import TestCase
from freezegun import freeze_time
from licenses.serializers import NotificationSerializer
from licenses.models import Notification

from .utils import get_clients_for, get_expiring_licenses_for


class TestManyUserNotification(TestCase):
    @freeze_time("2023-01-02 12:00:00")  # this date was a monday
    def setUp(self):
        self.users = [
            User.objects.create_user(
                username=f"user_{n}",
                email=f"user-{n}@email.com",
                password="password",
            )
            for n in range(3)
        ]
        self.clients = []
        for user in self.users:
            user_clients = get_clients_for(user)
            self.clients.extend(user_clients)

        self.lics = []
        for client in self.clients:
            licenses = get_expiring_licenses_for(client)
            self.lics.extend(licenses)

    def tearDown(self):
        for lic in self.lics:
            lic.delete()

        for client in self.clients:
            client.delete()

        for user in self.users:
            user.delete()

    def test_notification_log(self):
        # Prepare
        with freeze_time("2023-01-05 12:00:00"):
            self.client.post('/license-ms/notify/')

        with freeze_time("2023-01-02 12:00:00"):
            self.client.post('/license-ms/notify/')

        with freeze_time("2023-01-03 12:00:00"):
            self.client.post('/license-ms/notify/')

        url = "/license-ms/notifications/"

        # Execute
        response = self.client.get(url)

        # Assert Status
        self.assertEqual(response.status_code, 200)

        # Assert DB consistensy
        notifications = list(Notification.objects.all())
        self.assertEqual(len(response.data), len(notifications))

        # Assert Order
        notifications.sort(key=lambda notification: notification.send_datetime, reverse=True)

        expected_notifications = [
            NotificationSerializer(notification).data
            for notification in notifications
        ]

        self.assertListEqual(response.data, expected_notifications)

    def test_notification_log_limit(self):
        # Prepare
        with freeze_time("2023-01-05 12:00:00"):
            self.client.post('/license-ms/notify/')

        with freeze_time("2023-01-02 12:00:00"):
            self.client.post('/license-ms/notify/')

        with freeze_time("2023-01-03 12:00:00"):
            self.client.post('/license-ms/notify/')

        limit = 5
        url = f"/license-ms/notifications/?limit={limit}"

        # Execute
        response = self.client.get(url)

        # Assert Status
        self.assertEqual(response.status_code, 200)

        # Assert DB consistensy
        notifications = list(Notification.objects.all())
        self.assertEqual(len(response.data), limit)

        # Assert Order
        notifications.sort(key=lambda notification: notification.send_datetime, reverse=True)
        notifications = notifications[:5]

        expected_notifications = [
            NotificationSerializer(notification).data
            for notification in notifications
        ]

        self.assertListEqual(response.data, expected_notifications)

