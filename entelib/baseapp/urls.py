# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.http import HttpResponse, HttpResponseRedirect

def get_redirect_function_to_url(url):
    ''' Create response object which redirects client to given url. '''
    return (lambda request: HttpResponseRedirect(url))

def default(request):
    ''' This function is temporary here, in order to display sth else than admin page as default.'''
    return HttpResponse(u'<h1>Default page</h1> U can visit <a href="admin/">admin page</a> or <a href="admin/doc/">documentation</a> page, now.')


urlpatterns = patterns(
    '',

    # admin docs urls
    (r'admin/doc/', include('django.contrib.admindocs.urls')),
    (r'admin/doc$', get_redirect_function_to_url('/entelib/admin/doc/')),

    # admin panel urls
    (r'admin/', include(admin.site.urls)),
    (r'admin$',  get_redirect_function_to_url('/entelib/admin/')),

    # REPLACE ME: default matcher - to be replaced in future
    (r'', default),
)
