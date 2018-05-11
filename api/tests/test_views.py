from django.test import SimpleTestCase
from django.urls import reverse

import logging


class BruteForceListAddTests(SimpleTestCase):

    # Disable logging
    def setUp(self):
        logging.disable(logging.CRITICAL)

    # Reenable logging
    def tearDown(self):
        logging.disable(logging.NOTSET)

    # Test GET not allowed
    def test_get(self):
        response = self.client.get(reverse('add_key'))
        self.assertEqual(response.status_code, 405)

    # Test 400 on empty post
    def test_bad_request(self):
        response = self.client.post(reverse('add_key'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('This field is required.', str(response.content))

    # Test 200 successful add
    def test_add_key(self):
        key = 'this-is-an-ADD-Test'
        data = {
            'key': key,
        }
        upper_data = {
            'key': key.upper(),    # should be case insensitive
        }

        # Delete the entry in case it exists
        self.client.post(reverse('delete_key'), data)

        # Create the entry
        response = self.client.post(reverse('add_key'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['dn'])

        # Increment bad attempts
        response = self.client.post(reverse('add_key'), upper_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['umichExcListName'][0], key)
        self.assertEqual(response.json()['umichExcListBadAttempts'][0], '2')

        # Cleanup after ourselves
        self.client.post(reverse('delete_key'), data)


class BruteForceListFindTests(SimpleTestCase):

    # Disable logging
    def setUp(self):
        logging.disable(logging.CRITICAL)

    # Reenable logging
    def tearDown(self):
        logging.disable(logging.NOTSET)

    # Test GET not allowed
    def test_get(self):
        response = self.client.get(reverse('find_key'))
        self.assertEqual(response.status_code, 405)

    # Test 400 on empty post
    def test_bad_request(self):
        response = self.client.post(reverse('find_key'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('This field is required.', str(response.content))

    # Test 200 successful find
    def test_find_key(self):
        key = 'this-is-a-FIND-Test'
        data = {
            'key': key,
        }

        # Delete the entry if it exists
        self.client.post(reverse('delete_key'), data)

        # Create the entry so we can find it
        self.client.post(reverse('add_key'), data)

        # Find the entry
        response = self.client.post(reverse('find_key'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['umichExcListName'][0], key)
        self.assertEqual(response.json()['umichExcListBadAttempts'][0], '1')

        # Cleanup after ourselves
        self.client.post(reverse('delete_key'), data)


    # Test 404 not found
    def test_not_found(self):
        key = 'do-not-find-me'
        data = {
            'key': key,
        }
        response = self.client.post(reverse('find_key'), data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'not_found')
        self.assertEqual(response.json()['status'], 404)


class BruteForceListDeleteTests(SimpleTestCase):

    # Disable logging
    def setUp(self):
        logging.disable(logging.CRITICAL)

    # Reenable logging
    def tearDown(self):
        logging.disable(logging.NOTSET)

    # Test GET not allowed
    def test_get(self):
        response = self.client.get(reverse('delete_key'))
        self.assertEqual(response.status_code, 405)

    # Test 400 on empty post
    def test_bad_request(self):
        response = self.client.post(reverse('delete_key'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('This field is required.', str(response.content))

    # Test 200 successful delete
    def test_delete_key(self):
        key = 'this-is-a-DELETE-test'
        data = {
            'key': key,
        }

        # Create the entry so we can delete it
        self.client.post(reverse('add_key'), data)

        # Delete an existing entry
        response = self.client.post(reverse('delete_key'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'success')

        # Delete a non-existant entry
        response = self.client.post(reverse('delete_key'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], 'noSuchObject')


class UMIDExcListFindTests(SimpleTestCase):

    # Disable logging
    def setUp(self):
        logging.disable(logging.CRITICAL)

    # Reenable logging
    def tearDown(self):
        logging.disable(logging.NOTSET)

    # Test GET not allowed
    def test_get(self):
        response = self.client.get(reverse('find_umid'))
        self.assertEqual(response.status_code, 405)

    # Test 400 on empty post
    def test_bad_request(self):
        response = self.client.post(reverse('find_umid'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('This field is required.', str(response.content))

    # Test 200 successful find
    def test_find_umid(self):
        umid = '00133700'
        data = {
            'umid': umid,
        }
        response = self.client.post(reverse('find_umid'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['umichExcListName'][0], umid)
        self.assertEqual(response.json()['umichExcListManualLockout'][0], 'TRUE')

    # Test 404 not found
    def test_not_found(self):
        umid = '00111100'
        data = {
            'umid': umid,
        }
        response = self.client.post(reverse('find_umid'), data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['message'], 'not_found')
        self.assertEqual(response.json()['status'], 404)
