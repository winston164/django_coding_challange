from datetime import datetime
from django.test import TestCase
from django.core.serializers import serialize

from licenses.models import NotifyRequest
from licenses.serializers import NotifyRequestSerializer

# Create your tests here.

class NotFoundTest(TestCase):
    def test_404(self):

        # Prepare
        url = '/should-not-find'

        # Execute
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 404)

class TestNotifications(TestCase):
    def test_endpoint_reachable(self):

        # Prepare
        url = '/license-ms/notify/'

        # Execute
        response = self.client.post(url)

        # Assert 
        self.assertEqual(response.status_code, 200)

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

        notify_request: NotifyRequest = NotifyRequest.objects.get()
        notify_request = NotifyRequestSerializer(notify_request)

        self.assertEqual(response.data, notify_request.data)



