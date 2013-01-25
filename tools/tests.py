from django.test import TestCase

class ViewsTest(TestCase):
    def test_get_form(self):
      """ Get the main page """
      response = self.client.get("/")
