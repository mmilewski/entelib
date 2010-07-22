# -*- coding: utf-8 -*-
from django.test import TestCase
from page_logger import *
from entelib.dbconfigfiller import fill_config


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

    def test_user_list(self):
        self.login()
        self.failUnlessEqual(200, self.get_status_code('/entelib/users/'))
        
        ''' Test listing users. '''
        

    def test_books_list(self):
        ''' Tests listing books. '''
        url = '/entelib/books/'
        self.assert_(page_not_accessed(self.get_response(url)))     # no access for anonymous user
        self.login()                                                # but if we log in...
        self.assert_(page_accessed(self.get_response(url)))         # ... access is granted.


    def test_show_non_existance_book(self):
        ''' Shows first book '''
        url = '/entelib/books/0/'
        self.failUnlessEqual(302, self.get_status_code(url))  # redirect to login
        self.login()
        self.failUnlessEqual(404, self.get_status_code(url))  # now we see there no such book

    def test_login_urls_redirected_if_no_login(self):
        ''' Tests if you can see something without logging in '''
        for url, redirect_url in non_login_redirect_urls:
            response = self.client.get(url, follow=True)
            self.assertRedirects(response, redirect_url,\
                msg_prefix='Non login assertion failure: %s was not redirected to %s.' %\
                                                      ( (url),                (redirect_url) ) 
                                )


    def test_non_login_urls_accessed(self):
        ''' Tests if you can see those pages without logging in '''
        for url in non_login_urls:
            code = self.get_status_code(url)
            self.assertEqual(code, 200, "Page %s couldn\'t be accessed without loggin in." % url)
            

# pairs of form (ulr_a, url_b). If not logged in you should be redirected from url_a to url_b
_login_url = '/entelib/login/'
non_login_redirect_urls = [
    ('/entelib/login',                                  _login_url),
    ('/entelib/accounts/login/',                        _login_url),
    ('/entelib/accounts/login',                         _login_url),
    ('/entelib/users/',                                 _login_url + '?next=/entelib/users/'),
    ('/entelib/users/1/',                               _login_url + '?next=/entelib/users/1/'),
    ('/entelib/users/1/reservations/',                  _login_url + '?next=/entelib/users/1/reservations/'),
    ('/entelib/users/1/reservations/1/',                _login_url + '?next=/entelib/users/1/reservations/1/'),
    ('/entelib/users/1/reservations/new/',              _login_url + '?next=/entelib/users/1/reservations/new/'),
    ('/entelib/users/1/reservations/new/book/1/',       _login_url + '?next=/entelib/users/1/reservations/new/book/1/'),
    ('/entelib/users/1/reservations/new/bookcopy/1/',   _login_url + '?next=/entelib/users/1/reservations/new/bookcopy/1/'),
    ('/entelib/users/1/reservations/cancel-all/',       _login_url + '?next=/entelib/users/1/reservations/cancel-all/'),
    ('/entelib/users/1/rentals/',                       _login_url + '?next=/entelib/users/1/rentals/'),
    ('/entelib/profile/',                               _login_url + '?next=/entelib/profile/'),
    ('/entelib/profile/reservations/',                  _login_url + '?next=/entelib/profile/reservations/'),
    ('/entelib/profile/reservations/new/',              _login_url + '?next=/entelib/profile/reservations/new/'),
    ('/entelib/profile/reservations/cancel-all/',       _login_url + '?next=/entelib/profile/reservations/cancel-all/'),
    ('/entelib/profile/rentals/',                       _login_url + '?next=/entelib/profile/rentals/'),
    ('/entelib/books/',                                 _login_url + '?next=/entelib/books/'),
    ('/entelib/books',                                  _login_url + '?next=/entelib/books/'),
    ('/entelib/books/1/',                               _login_url + '?next=/entelib/books/1/'),
    ('/entelib/requestbook/',                           _login_url + '?next=/entelib/requestbook/'),
    ('/entelib/bookcopy/1/',                            _login_url + '?next=/entelib/bookcopy/1/'),
    ('/entelib/bookcopy/1/reserve/',                    _login_url + '?next=/entelib/bookcopy/1/reserve/'),
    ('/entelib/report/',                                _login_url + '?next=/entelib/report/'),
    ('/entelib/emaillog/',                              _login_url + '?next=/entelib/emaillog/'),
    ('/entelib/config/',                                _login_url + '?next=/entelib/config/'),
    ('/entelib/config/display_tips/',                   _login_url + '?next=/entelib/config/display_tips/'),
    ('/entelib/load_default_config/1/',                 _login_url + '?next=/entelib/load_default_config/1/'),
    ('/entelib/',                                       _login_url + '?next=/entelib/'),
    ('/entelib/logout',                                 _login_url + '?next=/entelib/'),
    ('/entelib/logout/',                                _login_url + '?next=/entelib/'),
    ('/entelib/admin',                                  '/entelib/admin/'),
    ]

non_login_urls = [
    '/quickhack',
    '/entelib/login/',
    '/entelib/register/newuser/',
    '/entelib/register/action/',
    '/entelib/admin/',
    ]
