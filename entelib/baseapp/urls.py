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
    return (lambda request, *args, **kwargs: HttpResponseRedirect(url))

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
    url(r'^users/$', view.show_users, name="user_all"),
    url(r'^users/add/$', view.add_user, name="user_add"),
    url(r'^users/(\d+)/$', view.show_user, name="user_one"),
    url(r'^users/(\d+)/activate/$', view.activate_user, name="activate_user"),
    (r'^users/(\d+)/reservations/$', view.show_user_reservations),
    (r'^users/(\d+)/reservations/archive/$', view.show_user_reservation_archive),
    (r'^users/(\d+)/reservations/(\d+)/$', view.show_user_reservation),
    (r'^users/(\d+)/reservations/new/$', get_redirect_function_to_url('../../books/')),
    (r'^users/(\d+)/books/$', view.find_book_for_user),
    (r'^users/(\d+)/books/(\d+)/$', view.find_book_for_user),
    (r'^users/(\d+)/bookcopy/(\d+)/$', view.reserve_for_user),
    (r'^users/(\d+)/bookcopy/(\d+)/reserve/$', get_redirect_function_to_url('../')),
    (r'^users/(\d+)/bookcopy/(\d+)/up/$', view.user_book_copy_up_link),
    (r'^users/(\d+)/reservations/cancel-all/$', view.cancel_all_user_reservations),
    # (r'^users/(\d+)/rent-book/(\d+)/$', view.show_user_reservation),
    # (r'^users/(\d+)/rent-book/$', view.user_list_books),
    (r'^users/(\d+)/rentals/$', view.show_user_rentals),
    (r'^users/(\d+)/rentals/new/$', get_redirect_function_to_url('../../books/')),
    (r'^users/(\d+)/rentals/archive/$', view.show_user_rental_archive),
    # (r'^users/(\d+)/rentals/(\d+)/$', view.user_rental),
    # (r'^users/(\d+)/books/$', view.user_books),

    # user profile
    url(r'^profile/$', view.edit_user_profile, name="profile_edit"),
    (r'^profile/reservations/$', view.show_my_reservations),
    (r'^profile/reservations/archive/$', view.show_my_reservation_archive),
    (r'^profile/reservations/new/$', view.my_new_reservation),
    (r'^profile/reservations/cancel-all/$', view.cancel_all_my_reserevations),
    (r'^profile/rentals/$', view.show_my_rentals),
    (r'^profile/rentals/new/$', view.my_new_reservation),
    (r'^profile/rentals/archive/$', view.show_my_rental_archive),

    # registration
    # (r'^register/$', view.register),
    (r'^register/(?P<action>(.+))/$', view.register),

    # books
    url(r'^books/$', view.show_books, name="book_all"),
    url(r'^books/(\d+)/$', view.show_book, name="book_one"),
    url(r'^books/(\d+)/edit/$', view.show_edit_book, name="book_edit"),
    url(r'^books/add/$', view.show_add_book, name="book_add"),
    (r'^requestbook/$', view.request_book),                   # request for book

    # book copies
    url(r'^bookcopy/(\d+)/$', view.show_book_copy, name="copy_one"),
    url(r'^bookcopy/(\d+)/edit/$', view.show_edit_bookcopy, name="copy_edit"),
    url(r'^bookcopy/add,(\d+)/$', view.show_add_bookcopy, name="copy_add"),
    (r'^bookcopy/(\d+)/up/$', view.book_copy_up_link),
    (r'^bookcopy/\d+/user/$', view.find_user_to_rent_him),
    (r'^bookcopy/(\d+)/user/(\d+)/$', view.reserve),
    (r'^bookcopy/(\d+)/reserve/$', view.reserve),
    # (r'^bookcopy/(\d+)/reserve/up/$', view.show_book_copy),

    # locations
    url(r'^locations/$', view.show_locations, name="location_all"),
    url(r'^locations/(\d+)/$', view.show_location, name="location_one"),

    # librarian work
    url(r'^shipment/$', view.show_shipment_requests, name="shipment"),
    url(r'^current_reservations/$', view.show_current_reservations, name="location_reservations_rentable"),
    url(r'^current_reservations/(?P<show_all>(all))/$', view.show_current_reservations, name="location_reservations_all"),

    # reports
    url(r'^report/$', view.show_reports, name="report_all"),
    # (r'^report/(?P<name>[\w_]+)/$', view.show_reports),
    url(r'^report/(?P<name>(status|most_often_rented|most_often_reserved|black_list|lost_books))/$', view.show_reports, name="report_one"),

    # email logs
    (r'^emaillog/$', view.show_email_log),

    # config
    url(r'^config/$', view.show_config_options, name="config_all"),
    url(r'^config/(?P<option_key>(\w+))/$', view.edit_config_option, name="config_edit_option"),
    url(r'^config/(?P<option_key>(\w+)),global/$', view.edit_config_option, {'is_global':True}, name="config_edit_global_option"),
    url(r'^profile/config/$', view.show_config_options_per_user, name='profile_config'),
    url(r'^profile/config/(?P<option_key>(\w+))/$', view.edit_config_option, name="profile_config_edit_option"),
    (r'load_default_config/(?P<do_it>(\d))?/?$', view.load_default_config),

    # admin panel urls
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/doc$', get_redirect_function_to_url('/entelib/admin/doc/')),
    (r'^admin/', include(admin.site.urls)),
    (r'^admin$', get_redirect_function_to_url('/entelib/admin/')),

    # default matcher
    (r'^$', view.default),
)
