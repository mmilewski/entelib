#-*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib.auth.views import login
from entelib.baseapp.views import list_books, show_book, logout, default
import entelib.baseapp.views as view
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
    (r'^logout/', view.logout),
    (r'^logout$',  get_redirect_function_to_url('/entelib/logout/')),

    # books
    (r'^books/$', view.list_books),
    (r'^books$',  get_redirect_function_to_url('/entelib/book/')),
    (r'^books/(\d+)/$', view.show_book),

    # book copies
    (r'^bookcopy/(\d+)/$', view.book_copy),


    # admin docs urls
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/doc$', get_redirect_function_to_url('/entelib/admin/doc/')),

    # admin panel urls
    ## allows to change password from CustomUserForm
    # (r'^admin/baseapp/customuser/(?P<uid>\d+)/(?P<rest>.+)', 'django.views.generic.simple.redirect_to', {'url': '/entelib/admin/auth/user/%(uid)s/%(rest)s'}),
    ## displays custom user when trying to show auth.user - ugly hack
    # (r'^admin/auth/user/(?P<uid>\d+)/$', 'django.views.generic.simple.redirect_to', {'url': '/entelib/admin/baseapp/customuser/%(uid)s/'}),
    ## redirects admin pages
    (r'^admin/', include(admin.site.urls)),
    (r'^admin$',  get_redirect_function_to_url('/entelib/admin/')),

    # REPLACE ME: default matcher - to be replaced in future
    (r'^$', view.default),     #
)
