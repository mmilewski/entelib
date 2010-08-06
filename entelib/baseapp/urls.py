# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib.auth.views import login as django_login
import entelib.baseapp.views as view
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()



def get_redirect_function_to_url(url):
    ''' Create response object which redirects client to given url. '''
    return (lambda request: HttpResponseRedirect(url))

urlpatterns = patterns(
    '',

    # login/logout
    (r'^login/', django_login),
    (r'^login$', get_redirect_function_to_url('/entelib/login/')),
    (r'^accounts/login/', get_redirect_function_to_url('/entelib/login/')),
    (r'^accounts/login$', get_redirect_function_to_url('/entelib/login/')),
    (r'^logout/', view.logout),
    (r'^logout$', get_redirect_function_to_url('/entelib/logout/')),

    # users
    (r'^users/$', view.show_users),
    (r'^users/add/$', view.add_user),
    (r'^users/(\d+)/$', view.show_user),
    (r'^users/(\d+)/reservations/$', view.show_user_reservations),
    (r'^users/(\d+)/reservations/archive/$', view.show_user_reservation_archive),
    (r'^users/(\d+)/reservations/(\d+)/$', view.show_user_reservation),
    (r'^users/(\d+)/reservations/new/$', view.find_book_for_user),
    (r'^users/(\d+)/reservations/new/books/(\d+)/$', view.find_book_for_user),
    (r'^users/(\d+)/reservations/new/bookcopy/(\d+)/$', view.reserve_for_user),
    (r'^users/(\d+)/reservations/new/bookcopy/(\d+)/up/$', view.user_book_copy_up_link),
    (r'^users/(\d+)/reservations/cancel-all/$', view.cancel_all_user_resevations),
    # (r'^users/(\d+)/rent-book/(\d+)/$', view.show_user_reservation),
    # (r'^users/(\d+)/rent-book/$', view.user_list_books),
    (r'^users/(\d+)/rentals/$', view.show_user_rentals),
    (r'^users/(\d+)/rentals/archive/$', view.show_user_rental_archive),
    # (r'^users/(\d+)/rentals/(\d+)/$', view.user_rental),
    # (r'^users/(\d+)/books/$', view.user_books),

    # user profile
    (r'^profile/$', view.edit_user_profile),
    (r'^profile/reservations/$', view.show_my_reservations),
    (r'^profile/reservations/archive/$', view.show_my_reservation_archive),
    (r'^profile/reservations/new/$', view.my_new_reservation),
    (r'^profile/reservations/cancel-all/$', view.cancel_all_my_reserevations),
    (r'^profile/rentals/$', view.show_my_rentals),
    (r'^profile/rentals/archive/$', view.show_my_rental_archive),

    # registration
    # (r'^register/$', view.register),
    (r'^register/(?P<action>(.+))/$', view.register),

    # books
    (r'^books/$', view.show_books),
    (r'^books$', get_redirect_function_to_url('/entelib/books/')),
    (r'^books/(\d+)/$', view.show_book),
    (r'^requestbook/$', view.request_book),                   # request for book

    # book copies
    (r'^bookcopy/(\d+)/$', view.show_book_copy),
    (r'^bookcopy/(\d+)/up/$', view.book_copy_up_link),
    (r'^bookcopy/\d+/user/$', view.show_users),
    (r'^bookcopy/(\d+)/user/(\d+)/$', view.reserve),
    (r'^bookcopy/(\d+)/reserve/$', view.reserve),
    (r'^bookcopy/(\d+)/reserve/up/$', view.show_book_copy),

    # locations
    (r'^locations/$', view.show_locations),
    (r'^locations/(\d+)/$', view.show_location),

    # reports
    (r'^report/$', view.show_reports),
    # (r'^report/(?P<name>[\w_]+)/$', view.show_reports),
    (r'^report/(?P<name>(status|most_often_rented|most_often_reserved|black_list|lost_books))/$', view.show_reports),

    # email logs
    (r'^emaillog/$', view.show_email_log),

    # config
    (r'^config/$', view.show_config_options),
    (r'^config/(?P<option_key>(\w+))/$', view.edit_config_option),
    (r'load_default_config/(?P<do_it>(\d))?/?$', view.load_default_config),

    # admin panel urls
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/doc$', get_redirect_function_to_url('/entelib/admin/doc/')),
    (r'^admin/', include(admin.site.urls)),
    (r'^admin$', get_redirect_function_to_url('/entelib/admin/')),

    # default matcher
    (r'^$', view.default),
)
