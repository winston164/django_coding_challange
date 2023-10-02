from django.test import TestCase

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

