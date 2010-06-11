# -*- coding: utf-8 -*-
from django.test import TestCase
from page_logger import *
from entelib.dbfiller import fill_config


class PageAccessTest(TestCase, PageLogger):
    '''
    Checks whether different urls where rendered properly.
    '''
    def setUp(self):
        self.config = fill_config()

    def test_index_page(self):
        ''' Tests correct redirection of index pages. '''
        self.failUnlessEqual(302, self.get_status_code('/entelib/'))  # redirects to login/
        self.failUnlessEqual(301, self.get_status_code('/'))          # redirects to login/

    def test_login_page(self):
        ''' Tests login url and appending slash at the end. '''
        self.assertEqual(200, self.get_status_code('/entelib/login/'))
        self.assertEqual(302, self.get_status_code('/entelib/login'))   # redirects to login/

    def test_admin_panel_page(self):
        ''' Tests few admin panel's urls. '''
        self.failUnlessEqual(200, self.get_status_code('/entelib/admin/'))
        self.failUnlessEqual(302, self.get_status_code('/entelib/admin'))
        self.failUnlessEqual(200, self.get_status_code('/entelib/admin/doc/'))
        self.failUnlessEqual(302, self.get_status_code('/entelib/admin/doc'))

    def test_books_list(self):
        ''' Tests listing books. '''
        url = '/entelib/books/'
        self.assert_(page_not_accessed(self.get_response(url)))     # no access for anonymous user
        self.login()                                                # but if we log in...
        self.assert_(page_accessed(self.get_response(url)))         # ... access is granted.
