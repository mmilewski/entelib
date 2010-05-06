from django.test import TestCase

class PageRenderedTest(TestCase):
    def get_status_code(self, url):
        from django.test.client import Client
        return Client().get(url).status_code

    def test_index_page(self):
        self.failUnlessEqual(302, self.get_status_code('/entelib/'))  # redirects to login/
        self.failUnlessEqual(301, self.get_status_code('/'))          # redirects to login/

    def test_login_page(self):
        self.assertEqual(200, self.get_status_code('/entelib/login/'))
        self.assertEqual(302, self.get_status_code('/entelib/login'))   # redirects to login/

    def test_admin_panel_page(self):
        self.failUnlessEqual(200, self.get_status_code('/entelib/admin/'))
        self.failUnlessEqual(302, self.get_status_code('/entelib/admin'))

    def test_admin_doc_page(self):
        self.failUnlessEqual(200, self.get_status_code('/entelib/admin/doc/'))
        self.failUnlessEqual(302, self.get_status_code('/entelib/admin/doc'))


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}


from config import Config
from baseapp.models import Configuration

class DbConfigTest(TestCase):
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
        
