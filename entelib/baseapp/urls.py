# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

def default(request):
    ''' This function is temporary here, in order to display sth else than admin page as default.'''
    from django.http import HttpResponse
    return HttpResponse(u'<h1>Default page</h1> U can visit <a href="admin/">admin page</a> or <a href="admin/doc/">documentation</a> page, now.')


urlpatterns = patterns(
    '',
    # Example:
    # (r'^entelib/', include('entelib.foo.urls')),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    (r'admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'admin/', include(admin.site.urls)),

    # REPLACE ME: default matcher - to be replaced in future
    (r'', default),
)
