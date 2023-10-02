from django.test import TestCase

# Create your tests here.

class NotFoundTest(TestCase):
    def test_404(self):

        # Use non-existent view
        url = '/should-not-find'

        # Assert response
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


