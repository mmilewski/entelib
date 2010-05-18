# -*- coding: utf-8 -*-
from django.conf import settings


def page_accessed(response):
    '''
    Checks whether page was rendered - we could access it. Returns True on success.
    If page wasn't found (404, 500, ...) returns False.
    Redirection is neither True nor False.
    '''
    if not page_exists(response):
        return False
    return 'Forbidden' not in response.content


def page_not_accessed(response):
    '''
    Returns True if page couldn't be accessed, but False if an error occured.
    Note that if page doesn't exist, it means error, so function returns False.
    Redirection to login page ==> perm wasn't granted ==> page not accessed ==> return True.
    '''
    if not page_exists(response):
        return False
    if was_redirected(response, settings.LOGIN_URL):
        return True
    return not page_accessed(response)


def page_exists(response):
    ''' Checks unless 404 or 500 occured. '''
    return response.status_code not in [404, 500]


def was_redirected(response, url_suffix=None):
    '''
    Returns True if response carries redirection info.
    If url_suffix is set, then redirection's Location's suffix have to match url_suffix, and it is omitted otherwise.
    '''
    if not url_suffix:
        url_suffix = ''
    return response.status_code in [301, 302] and response['Location'].endswith(url_suffix)


class PageLogger(object):
    '''
    Handles user logging in and allows to assert reponse for given url.
    '''

    fixtures = ['logindata.json']
    username = 'testname'
    userpassword = 'admin'

    def login(self, username=username, password=userpassword):
        ''' Logs user 'username' with 'password' in. Fails if login was not possible. '''
        response = self.get_post_response('/entelib/login/', {'username': username, 'password': password})
        self.assertEquals(302, response.status_code)       # no redirection is login failure, so we require it
        self.assert_(response['Location'].endswith(settings.LOGIN_REDIRECT_URL))

    def get_status_code(self, url):
        ''' Returns status code of page requested with GET method. '''
        return self.get_response(url).status_code

    def get_post_status_code(self, url, post_data={}):
        ''' Returns status code of page requested with POST method. '''
        return self.get_post_response(url, post_data).status_code

    def get_response(self, url):
        ''' Returns response using GET method. '''
        return self.client.get(url)

    def get_post_response(self, url, post_data={}):
        ''' Returns response using POST method. '''
        return self.client.post(url, post_data)
