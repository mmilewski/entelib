#-*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib.auth.views import login
from entelib.baseapp.views import list_books, show_book, logout, default
from django.shortcuts import render_to_response
from django.template import RequestContext
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.http import HttpResponse, HttpResponseRedirect

def get_redirect_function_to_url(url):
    ''' Create response object which redirects client to given url. '''
    return (lambda request: HttpResponseRedirect(url))

urlpatterns = patterns(
    '',

    # login/logout
    (r'^login/', login),
    (r'^login$',  get_redirect_function_to_url('/entelib/login/')),
    (r'^accounts/login/',  get_redirect_function_to_url('/entelib/login/')),
    (r'^accounts/login$',  get_redirect_function_to_url('/entelib/login/')),
    (r'^logout/', logout),
    (r'^logout$',  get_redirect_function_to_url('/entelib/logout/')),

    # books
    (r'^books/$', list_books),
    (r'^books$',  get_redirect_function_to_url('/entelib/book/')),
    (r'^books/(\d)/$', show_book),


    # admin docs urls
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/doc$', get_redirect_function_to_url('/entelib/admin/doc/')),

    # admin panel urls
    (r'^admin/', include(admin.site.urls)),
    (r'^admin$',  get_redirect_function_to_url('/entelib/admin/')),

    # 
    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 
        'django.views.static.serve',
        { 'document_root': settings.MEDIA_ROOT, }
    ),

    # REPLACE ME: default matcher - to be replaced in future
    (r'', default),
)
