from django.test import TestCase

class PageRenderedTest(TestCase):
    def get_status_code(self, url):
        from django.test.client import Client
        return Client().get(url).status_code

    def test_index_page(self):
        self.failUnlessEqual(200, self.get_status_code('/entelib/'))

    def test_admin_panel_page(self):
        self.failUnlessEqual(200, self.get_status_code('/entelib/admin/'))
        # 302 code = url was redirected
        self.failUnlessEqual(302, self.get_status_code('/entelib/admin'))

    def test_admin_doc_page(self):
        self.failUnlessEqual(200, self.get_status_code('/entelib/admin/doc/'))
        self.failUnlessEqual(302, self.get_status_code('/entelib/admin/doc'))


__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

