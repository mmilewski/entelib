# -*- coding: utf-8 -*-
from django.test import TestCase
from page_logger import *
from entelib.dbconfigfiller import fill_config
from baseapp.config import Config
from test_base import Test

# class PageAccessTest(TestCase, PageLogger):
class PageAccessTest(Test):
    '''
    Checks whether different urls where rendered properly.
    '''
    def setUp(self):
        # self.config = fill_config()
        self.config = Config()

    def test_index_page(self):
        ''' Tests correct redirection of index pages. '''
        self.failUnlessEqual(302, self.get_status_code('/entelib/'))  # redirects to login/
        self.failUnlessEqual(301, self.get_status_code('/'))          # redirects to login/

    def test_login_page(self):
        ''' Tests login url and appending slash at the end. '''
        self.assertEqual(200, self.get_status_code('/entelib/login/'))
        self.assertEqual(302, self.get_status_code('/entelib/login'))   # redirects to login/

    def test_admin_panel_page(self):
        """ Tests few admin panel's urls. """
        self.failUnlessEqual(200, self.get_status_code('/entelib/admin/'))
        self.failUnlessEqual(302, self.get_status_code('/entelib/admin'))
        self.failUnlessEqual(200, self.get_status_code('/entelib/admin/doc/'))
        self.failUnlessEqual(302, self.get_status_code('/entelib/admin/doc'))

    def test_user_list(self):
        # self.login()
        self.log_lib()
        self.failUnlessEqual(200, self.get_status_code('/entelib/users/'))
        
        ''' Test listing users. '''
        

    def test_books_list(self):
        ''' Tests listing books. '''
        url = '/entelib/books/'
        self.assert_(page_not_accessed(self.get_response(url)))     # no access for anonymous user
        # self.login()
        self.log_user()
        self.assert_(page_accessed(self.get_response(url)))         # ... access is granted.


    def test_show_non_existance_book(self):
        ''' Shows first book '''
        url = '/entelib/books/0/'
        self.failUnlessEqual(302, self.get_status_code(url))  # redirect to login
        # self.login()
        self.log_user()
        self.failUnlessEqual(404, self.get_status_code(url))  # now we see there no such book


    def test_various_urls_accessed(self):
        self.log_admin()
        def page_was_displayed(url):
            from baseapp.tests.views import accessed
            response = self.client.get(url)
            self.assert_(accessed(response))

        page_was_displayed('/entelib/books/')
        page_was_displayed('/entelib/books/add/')
        page_was_displayed('/entelib/books/1/edit/')
        
        page_was_displayed('/entelib/categories/')
        page_was_displayed('/entelib/categories/add/')
        page_was_displayed('/entelib/categories/1/edit/')

        page_was_displayed('/entelib/authors/')
        page_was_displayed('/entelib/authors/add/')
        page_was_displayed('/entelib/authors/1/edit/')
        
        page_was_displayed('/entelib/publishers/')
        page_was_displayed('/entelib/publishers/add/')
        page_was_displayed('/entelib/publishers/1/edit/')
        
        page_was_displayed('/entelib/costcenters/')
        page_was_displayed('/entelib/costcenters/add/')
        page_was_displayed('/entelib/costcenters/1/edit/')
        
        page_was_displayed('/entelib/locations/')
        page_was_displayed('/entelib/locations/add/')
        
        page_was_displayed('/entelib/buildings/')
        page_was_displayed('/entelib/buildings/add/')
        page_was_displayed('/entelib/buildings/1/edit/')
        
        page_was_displayed('/entelib/users/')
        page_was_displayed('/entelib/users/1/')
        page_was_displayed('/entelib/users/1/reservations/')
        page_was_displayed('/entelib/users/1/books/1/')
        page_was_displayed('/entelib/users/1/bookcopy/1/')
        page_was_displayed('/entelib/users/1/reservations/cancel-all/')
        page_was_displayed('/entelib/users/1/rentals/')
        page_was_displayed('/entelib/profile/')
        page_was_displayed('/entelib/profile/reservations/')
        page_was_displayed('/entelib/profile/')
        page_was_displayed('/entelib/profile/reservations/cancel-all/')
        page_was_displayed('/entelib/profile/rentals/')
        page_was_displayed('/entelib/locations/')
        page_was_displayed('/entelib/locations/1/')
        page_was_displayed('/entelib/books/')
        page_was_displayed('/entelib/books/1/')
        page_was_displayed('/entelib/books/1/edit/')
        page_was_displayed('/entelib/bookrequests/')
        page_was_displayed('/entelib/bookrequests/add/')
        page_was_displayed('/entelib/bookcopy/1/')
        page_was_displayed('/entelib/bookcopy/1/edit/')
        page_was_displayed('/entelib/bookcopy/1/reserve/')
        page_was_displayed('/entelib/report/')
        page_was_displayed('/entelib/emaillog/')
        page_was_displayed('/entelib/config/')
        page_was_displayed('/entelib/config/display_tips/')

    def test_login_urls_redirected_if_no_login(self):
        ''' Tests if you can see something without logging in '''
        self.logout()
        for url, redirect_url in non_login_redirect_urls:
            response = self.client.get(url, follow=True)

            # django supports only 302 as redirection code. This functionality could be extracted somwhere
            if response.redirect_chain and (response.redirect_chain[0][1] in [301, 302]):
                url,code = response.redirect_chain[0]
                response.redirect_chain[0] = (url, 302)

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
    ('/entelib/users/1/books/1/',                       _login_url + '?next=/entelib/users/1/books/1/'),
    ('/entelib/users/1/bookcopy/1/',                    _login_url + '?next=/entelib/users/1/bookcopy/1/'),
    ('/entelib/users/1/reservations/cancel-all/',       _login_url + '?next=/entelib/users/1/reservations/cancel-all/'),
    ('/entelib/users/1/rentals/',                       _login_url + '?next=/entelib/users/1/rentals/'),
    ('/entelib/profile/',                               _login_url + '?next=/entelib/profile/'),
    ('/entelib/profile/reservations/',                  _login_url + '?next=/entelib/profile/reservations/'),
    ('/entelib/profile/',                               _login_url + '?next=/entelib/profile/'),
    ('/entelib/profile/reservations/cancel-all/',       _login_url + '?next=/entelib/profile/reservations/cancel-all/'),
    ('/entelib/profile/rentals/',                       _login_url + '?next=/entelib/profile/rentals/'),
    ('/entelib/locations/',                             _login_url + '?next=/entelib/locations/'),
    ('/entelib/locations/1/',                           _login_url + '?next=/entelib/locations/1/'),
    ('/entelib/books/',                                 _login_url + '?next=/entelib/books/'),
    ('/entelib/books',                                  _login_url + '?next=/entelib/books/'),
    ('/entelib/books/1/',                               _login_url + '?next=/entelib/books/1/'),
    ('/entelib/books/1/edit/',                          _login_url + '?next=/entelib/books/1/edit/'),
    ('/entelib/bookrequests/',                          _login_url + '?next=/entelib/bookrequests/'),
    ('/entelib/bookrequests/add/',                      _login_url + '?next=/entelib/bookrequests/add/'),
    ('/entelib/bookcopy/1/',                            _login_url + '?next=/entelib/bookcopy/1/'),
    ('/entelib/bookcopy/1/edit/',                       _login_url + '?next=/entelib/bookcopy/1/edit/'),
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

def add_non_login_redirect_url(url):
    non_login_redirect_urls.append(  (url, _login_url+'?next='+url)  )

add_non_login_redirect_url('/entelib/books/')
add_non_login_redirect_url('/entelib/books/add/')
add_non_login_redirect_url('/entelib/books/1/edit/')

add_non_login_redirect_url('/entelib/categories/')
add_non_login_redirect_url('/entelib/categories/add/')
# add_non_login_redirect_url('/entelib/categories/1/edit/')

add_non_login_redirect_url('/entelib/authors/')
add_non_login_redirect_url('/entelib/authors/add/')
# add_non_login_redirect_url('/entelib/authors/1/edit/')

add_non_login_redirect_url('/entelib/publishers/')
add_non_login_redirect_url('/entelib/publishers/add/')
# add_non_login_redirect_url('/entelib/publishers/1/edit/')

add_non_login_redirect_url('/entelib/costcenters/')
add_non_login_redirect_url('/entelib/costcenters/add/')
# add_non_login_redirect_url('/entelib/costcenters/1/edit/')

add_non_login_redirect_url('/entelib/locations/')
add_non_login_redirect_url('/entelib/locations/add/')
# add_non_login_redirect_url('/entelib/locations/1/edit/')

add_non_login_redirect_url('/entelib/buildings/')
add_non_login_redirect_url('/entelib/buildings/add/')
# add_non_login_redirect_url('/entelib/buildings/1/edit/')


non_login_urls = [
    '/entelib/login/',
    '/entelib/register/newuser/',
    '/entelib/register/action/',
    '/entelib/admin/',
    ]
