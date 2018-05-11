from django.test import SimpleTestCase

from ..exc_list_manager import exc_list_find_umid, exc_list_find_key, exc_list_add_key, exc_list_delete_key, ExcListError

import logging


class ExcListTests(SimpleTestCase):

    # Disable logging
    def setUp(self):
        logging.disable(logging.CRITICAL)

    # Reenable logging
    def tearDown(self):
        logging.disable(logging.NOTSET)

    # Test finds on umid
    def test_find_umid(self):
        umid = '00133700'

        # Find an existing entry
        entry = exc_list_find_umid(umid)
        self.assertEqual(entry['umichExcListName'][0], umid)

        # Find a non-existent entry
        with self.assertRaises(ExcListError) as context:
            exc_list_find_umid('00111100')
        self.assertEqual(context.exception.message, 'not_found')

    # Test finds on key
    def test_find_key(self):
        key = 'find-me'

        # Create the entry
        exc_list_add_key(key)
        
        # Find the entry
        entry = exc_list_find_key(key)
        self.assertEqual(entry['umichExcListName'][0], key)

        # Delete the entry
        exc_list_delete_key(key)

        # Find the non-existent entry
        with self.assertRaises(ExcListError) as context:
            exc_list_find_key(key)
        self.assertEqual(context.exception.message, 'not_found')

    # Test adds on key
    def test_add_key(self):
        key = 'add-me'

        # Start with nothing
        exc_list_delete_key(key)

        # Create the entry
        response = exc_list_add_key(key)
        self.assertTrue(response['dn'])
        #self.assertEqual(entry['umichExcListName'][0], key)
        #self.assertEqual(entry['umichExcListBadAttempts'][0], '1')

        # Increment badAttempts
        entry = exc_list_add_key(key)
        self.assertEqual(entry['umichExcListName'][0], key)
        self.assertEqual(entry['umichExcListBadAttempts'][0], '2')

        # Cleanup
        exc_list_delete_key(key)

    # Test deletes on key
    def test_delete_key(self):
        key = 'delete-me'

        # Create the entry
        exc_list_add_key(key)

        # Delete the entry
        entry = exc_list_delete_key(key)
        self.assertEqual(entry['message'], 'success')

        # Delete non-existent entry
        entry = exc_list_delete_key(key)
        self.assertEqual(entry['message'], 'noSuchObject')

