from django.test import SimpleTestCase

from ..serializers import ExcListUMIDSerializer, ExcListKeySerializer


class UMIDSerializerTests(SimpleTestCase):

    # Test validation
    def test_valid_data(self):
        umid = '00123400'    # leading and trailing zeroes
        serializer = ExcListUMIDSerializer(data={
            'umid': umid,
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['umid'], umid)

    # Test for all required fields
    def test_blank_data(self):
        serializer = ExcListUMIDSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['umid'], ['This field is required.'])

    # Test for invalid data
    def test_invalid_data(self):
        serializer = ExcListUMIDSerializer(data={
            'umid': 'abc123',
        })
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['umid'], ['Enter a valid UMID.'])


class KeySerializerTests(SimpleTestCase):

    # Test validation
    def test_valid_data(self):
        key = '00-this-is-my-key-00'    # leading and trailing zeroes
        serializer = ExcListKeySerializer(data={
            'key': key,
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['key'], key)

    # Test for all required fields
    def test_blank_data(self):
        serializer = ExcListKeySerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['key'], ['This field is required.'])

