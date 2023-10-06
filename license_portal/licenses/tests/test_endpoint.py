from django.test import TestCase
from freezegun import freeze_time

from licenses.models import NotifyRequest

class NotFoundTest(TestCase):
    def test_404(self):

        # Prepare
        url = '/should-not-find'

        # Execute
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 404)

class TestNotificationsEndpiont(TestCase):

    def test_endpoint_reachable(self):

        # Prepare
        url = '/license-ms/notify/'

        # Execute
        response = self.client.post(url)

        # Assert 
        self.assertEqual(response.status_code, 200)

    @freeze_time('2023-01-01 12:00:00')
    def test_no_notifications(self):
        """ request with no objects in the database should only return request_datetime
        """

        # Prepare
        url = '/license-ms/notify/'


        # Execute
        response = self.client.post(url)

        # Assert 
        self.assertEqual(response.status_code, 200)
        self.assertEqual(NotifyRequest.objects.count(), 1)


        self.assertEqual(response.data, {
            "request_datetime": '2023-01-01T12:00:00Z',
            "notifications": []
        })
