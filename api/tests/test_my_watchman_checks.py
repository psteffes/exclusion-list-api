from django.test import SimpleTestCase

from ..exc_list_manager import ExcList, ExcListError

import logging


class HealthCheckTests(SimpleTestCase):

    # Disable logging
    def setUp(self):
        logging.disable(logging.CRITICAL)

    # Reenable logging
    def tearDown(self):
        logging.disable(logging.NOTSET)

    # ping pong
    def test_ping(self):
        response = self.client.get('/health/ping/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'pong')

    # Test Full Health Check
    def test_health(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
