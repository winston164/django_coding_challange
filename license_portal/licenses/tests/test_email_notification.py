from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from django.core import mail as django_email
from freezegun import freeze_time
from licenses.notifications import EmailNotification
from licenses.models import (
    Client,
    License,
    LicenseType,
    Notification,
    NotificationTopic,
    Package,
)


class TestEmailNotification(TestCase):

    @freeze_time("2023-01-01 12:00:00")
    def test_email_notifcation(self):

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
        lic2 =  License.objects.create(
            client=client,
            package=Package.ios_sdk,
            license_type=LicenseType.production,
            expiration_datetime=timezone.now() + timezone.timedelta(days=6),
        )
        lic3 =  License.objects.create(
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
        expected_email_body= f"""<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Generated with the help of ChatGPT-->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{notification.get_topic_display()}</title>
</head>
<body>
    <p>Hello {user.username},</p>

    <p>We wanted to inform you that some of your client {str(client)} licenses are about to expire soon. Please review the following details:</p>

    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Package</th>
                <th>Expiration Date</th>
            </tr>
        </thead>
        <tbody>
            
            <tr>
                <td>{ lic1.id }</td>
                <td>{ lic1.get_license_type_display() }</td>
                <td>{ lic1.get_package_display() }</td>
                <td>{ lic1.expiration_datetime.strftime("%Y-%m-%d") }</td>
            </tr>
            
            <tr>
                <td>{ lic2.id }</td>
                <td>{ lic2.get_license_type_display() }</td>
                <td>{ lic2.get_package_display() }</td>
                <td>{ lic2.expiration_datetime.strftime("%Y-%m-%d") }</td>
            </tr>
            
            <tr>
                <td>{ lic3.id }</td>
                <td>{ lic3.get_license_type_display() }</td>
                <td>{ lic3.get_package_display() }</td>
                <td>{ lic3.expiration_datetime.strftime("%Y-%m-%d") }</td>
            </tr>
            
        </tbody>
    </table>

    <p>Please take the necessary actions to renew or update these licenses to ensure uninterrupted service for your client.</p>

    <p>Thank you for your attention to this matter.</p>

    <p>Sincerely,<br>
    Afiniteam</p>
</body>
</html>"""

        # Execute
        notification_email = EmailNotification(notification)
        notification_email.send_notification(user.email)

        # Assert
        self.assertEqual(len(django_email.outbox), 1)

        sent_email = django_email.outbox[0]
        self.assertEqual(sent_email.subject, notification.get_topic_display())


        self.assertEqual(sent_email.from_email, 'noreply@email.com')
        self.assertEqual(sent_email.to, [user.email])

        body = sent_email.body.splitlines()
        expected_body = expected_email_body.splitlines()

        self.assertEqual(len(body), len(expected_body) )
        self.assertListEqual(body, expected_body)
