from django.test import TestCase
from django.conf import settings

from baseapp.config import Config
from baseapp.models import Configuration


class DbConfigTest(TestCase):
    '''
    Tests for configuration stored in database and accessed via Config module.
    '''

    def setUp(self):
        self.c = Config()
        record = Configuration(key='most_funny_number', value='8')
        record.save()

    def test_get_existing_key(self):
        self.assertEqual('8', self.c['most_funny_number'])

    def test_setting_value(self):
        self.c['almost_random_prefix'] = 'tralala'
        self.assertEqual('tralala', self.c['almost_random_prefix'])

    def test_containing(self):
        self.assertTrue('most_funny_number' in self.c)

    def test_get_int(self):
        self.assertEqual(8, self.c.get_int('most_funny_number'))

    def test_updating_int(self):
        self.c['most_funny_number'] = 42
        self.assertEqual(type(42), type(self.c.get_int('most_funny_number')))
        self.assertEqual(42, self.c.get_int('most_funny_number'))

    def test_creating_int(self):
        self.c['some_int_name'] = 123654
        self.assertEqual(123654, self.c.get_int('some_int_name'))
