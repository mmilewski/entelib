# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponsePermanentRedirect
import re


def accessed(response):
    """
    Use self.assert_(accessed(response)) to check if page wasn't redirected to login,
    because lack of perms or sth.

    Returns:
        True - page rendered properly
        False - request redirected to login page
    """
    login_infix = '/entelib/login/'
    if isinstance(response, HttpResponseNotFound):   # not found, so also not accessed
        return False
    if isinstance(response, HttpResponsePermanentRedirect):
        if 'Location' not in response:
            return False
        return login_infix not in response['Location']
    if isinstance(response, HttpResponseRedirect):
        return login_infix not in response['Location']
    rc = response.redirect_chain
    if not rc:
        return True
    return login_infix not in rc[-1][0]
    

def choice(collection):
    ''' Simplified pseudo-choice ensuring repeatable results. '''
    lst = list(collection)
    length = len(lst)
    seed = 117
    index = (seed % length) ** 3 % length
    return lst[index]


def form_errors_happened(html):
    ''' Checks if html contains form errors. '''
    return re.compile('<form.*error.*</form>', re.I).match(html)

def no_form_errors_happened(html):
    return not form_errors_happened(html)
