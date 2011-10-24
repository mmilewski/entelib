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
    (r'^accounts/login/', get_redirect_function_to_url('/entelib/login/')),
    (r'^accounts/login$', get_redirect_function_to_url('/entelib/login/')),
    (r'^login/', django_login),
    (r'^login$', get_redirect_function_to_url('/entelib/login/')),
    (r'^logout/', view.logout),
    (r'^logout$', get_redirect_function_to_url('/entelib/logout/')),
    # (r'^register/$', view.register),
    (r'^register/(?P<action>(.+))/$', view.register),
    url(r'forgot_password/$', view.show_forgot_password, name="forgot_password"),

    # users
    url(r'^users/$', view.show_users, name="user_all"),
    url(r'^users/add/$', view.add_user, name="user_add"),
    url(r'^users/(\d+)/$', view.show_user, name="user_one"),
    url(r'^users/(\d+)/activate/$', view.activate_user, name="activate_user"),
    url(r'^users/(\d+)/deactivate/$', view.deactivate_user, name="deactivate_user"),
    (r'^users/(\d+)/reservations/$', view.show_user_reservations),
    (r'^users/(\d+)/reservations/archive/$', view.show_user_reservation_archive),
    (r'^users/(\d+)/reservations/(\d+)/$', view.show_user_reservation),
    (r'^users/(\d+)/reservations/new/$', get_redirect_function_to_url('../../books/')),
    (r'^users/(\d+)/books/$', view.find_book_for_user),
    (r'^users/(\d+)/books/(\d+)/$', view.find_book_for_user),
    (r'^users/(\d+)/bookcopy/(\d+)/$', view.reserve_for_user),
    (r'^users/(\d+)/bookcopy/(\d+)/reserve/$', get_redirect_function_to_url('../')),
    (r'^users/(\d+)/bookcopy/(\d+)/up/$', view.user_book_copy_up_link),
    url(r'^users/(\d+)/reservations/cancel-all/$', view.cancel_all_user_reservations, name='cancel_all'),
    # (r'^users/(\d+)/rent-book/(\d+)/$', view.show_user_reservation),
    # (r'^users/(\d+)/rent-book/$', view.user_list_books),
    (r'^users/(\d+)/rentals/$', view.show_user_rentals),
    (r'^users/(\d+)/rentals/new/$', get_redirect_function_to_url('../../books/')),
    (r'^users/(\d+)/rentals/archive/$', view.show_user_rental_archive),
    # (r'^users/(\d+)/rentals/(\d+)/$', view.user_rental),
    # (r'^users/(\d+)/books/$', view.user_books),
    url(r'^users/activate/$', view.activate_many_users, name='activate_many_users'),

    # user profile
    url(r'^profile/$',                          view.edit_user_profile, name="profile_edit"),
    url(r'^profile/reservations/$',             view.show_my_reservations),
    url(r'^profile/reservations/archive/$',     view.show_my_reservation_archive),
    url(r'^profile/reservations/new/$',         view.my_new_reservation),
    url(r'^profile/reservations/cancel-all/$',  view.cancel_all_my_reserevations),
    url(r'^profile/rentals/$',                  view.show_my_rentals, name="my_rentals"),
    url(r'^profile/rentals/new/$',              view.my_new_reservation),
    url(r'^profile/rentals/archive/$',          view.show_my_rental_archive),
    url(r'^profile/onleave/$',                  view.onleave),

    # authors, categories, publishers, cost centers, states
    url(r'^authors/$',             view.show_authors,     name="author_all"),
    url(r'^authors/(\d+)/$',       view.show_author,      name="author_one"),
    url(r'^authors/(\d+)/edit/$',  view.show_edit_author, name="author_edit"),
    url(r'^authors/add/$',         view.show_add_author,  name="author_add"),

    url(r'^categories/$',             view.show_categories,    name="category_all"),
    url(r'^categories/(\d+)/$',       view.show_category,      name="category_one"),
    url(r'^categories/(\d+)/edit/$',  view.show_edit_category, name="category_edit"),
    url(r'^categories/add/$',         view.show_add_category,  name="category_add"),

    url(r'^publishers/$',             view.show_publishers,     name="publisher_all"),
    url(r'^publishers/(\d+)/$',       view.show_publisher,      name="publisher_one"),
    url(r'^publishers/(\d+)/edit/$',  view.show_edit_publisher, name="publisher_edit"),
    url(r'^publishers/add/$',         view.show_add_publisher,  name="publisher_add"),

    url(r'^costcenters/$',             view.show_costcenters,     name="costcenter_all"),
    url(r'^costcenters/(\d+)/$',       view.show_costcenter,      name="costcenter_one"),
    url(r'^costcenters/(\d+)/edit/$',  view.show_edit_costcenter, name="costcenter_edit"),
    url(r'^costcenters/add/$',         view.show_add_costcenter,  name="costcenter_add"),

    url(r'^states/$',             view.show_states,     name="state_all"),
    url(r'^states/(\d+)/$',       view.show_state,      name="state_one"),
    url(r'^states/(\d+)/edit/$',  view.show_edit_state, name="state_edit"),
    url(r'^states/add/$',         view.show_add_state,  name="state_add"),

    # locations, buildings
    url(r'^locations/$',        view.show_locations,     name="location_all"),
    url(r'^locations/(\d+)/$',  view.show_location,      name="location_one"),
    url(r'^locations/(\d+)/$',  view.show_location,      name="location_edit"),
    url(r'^locations/add/$',    view.show_add_location,  name="location_add"),

    url(r'^buildings/$',             view.show_buildings,     name="building_all"),
    url(r'^buildings/(\d+)/$',       view.show_building,      name="building_one"),
    url(r'^buildings/(\d+)/edit/$',  view.show_edit_building, name="building_edit"),
    url(r'^buildings/add/$',         view.show_add_building,  name="building_add"),

    # books
    url(r'^books/$',                 view.show_books,          name="book_all"),
    url(r'^books/(\d+)/$',           view.show_book,           name="book_one"),
    url(r'^books/(\d+)/edit/$',      view.show_edit_book,      name="book_edit"),
    url(r'^books/add/$',             view.show_add_book,       name="book_add"),

    # book requests
    url(r'^bookrequests/$',              view.show_bookrequests_active,  name="bookrequest_active"),
    url(r'^bookrequests/alsoarchival/$', view.show_bookrequests,         name="bookrequest_all"),
    url(r'^bookrequests/(\d+)/$',        view.show_bookrequest,          name="bookrequest_one"),
    url(r'^bookrequests/(\d+)/edit/$',   view.show_edit_bookrequest,     name="bookrequest_edit"),
    url(r'^bookrequests/add/$',          view.show_add_bookrequest,      name="bookrequest_add"),
    url(r'^bookrequests/add/$',          view.show_add_bookrequest,      name="bookrequest_add_book"),
    url(r'^bookrequests/add,(\d+)/$',    view.show_add_bookrequest,      name="bookrequest_add_copy"),

    # book copies
    url(r'^bookcopy/(\d+)/$',             view.show_book_copy,       name="copy_one"),
    url(r'^bookcopy/(\d+)/edit/$',        view.show_edit_bookcopy,   name="copy_edit"),
    url(r'^bookcopy/add,(\d+)/$',         view.show_add_bookcopy,    name="copy_add"),
    url(r'^bookcopy/(\d+)/up/$',          view.book_copy_up_link),
    url(r'^bookcopy/\d+/user/$',          view.find_user_to_rent_him),
    url(r'^bookcopy/(\d+)/user/(\d+)/$',  view.reserve,                              name="reserve_for_user"),
    url(r'^bookcopy/(\d+)/user/(\d+)/up/$',  get_redirect_function_to_url('../..'),  name="reserve_for_user_go_up"),
    url(r'^bookcopy/(\d+)/reserve/$',     view.reserve,                              name="reserve"),
    url(r'^bookcopy/(\d+)/reserve/up/$',  get_redirect_function_to_url('../..'),     name="reserve_go_up"),
    # (r'^bookcopy/(\d+)/reserve/up/$', view.show_book_copy),

    # librarian work
    url(r'^shipment/$', view.show_shipment_requests, name="shipment"),
    url(r'^current_reservations/$', view.show_current_reservations, name="librarian_reservations_rentable"),
    url(r'^current_reservations/(?P<show_all>(all))/$', view.show_current_reservations, name="librarian_reservations_all"),
    url(r'^current_rentals/$', view.show_current_rentals, name='current_librarian_rentals'),

    # reports
    url(r'^report/$', view.show_reports, name="report_all"),
    # (r'^report/(?P<name>[\w_]+)/$', view.show_reports),
    url(r'^report/(?P<name>(status|most_often_rented|most_often_reserved|black_list|lost_books))/$', view.show_reports, name="report_one"),

    # email logs
    url(r'^emaillog/$',                 get_redirect_function_to_url('/entelib/emaillog/latest,200/'),   name="emaillog"),
    url(r'^emaillog/all/$',             view.show_email_log, {'show_all':True},                          name="emaillog_all"),
    url(r'^emaillog/latest,(\d+)/$',    view.show_email_log,                                             name="emaillog_latest"),

    # config
    url(r'^config/$',                    view.show_config_options,                    name="config_all"),
    url(r'^config/(\w+)/$',              view.edit_config_option,                     name="config_edit_option"),
    url(r'^config/(\w+),global/$',       view.edit_config_option, {'is_global':True}, name="config_edit_global_option"),
    url(r'^profile/config/$',            view.show_config_options_per_user,           name='profile_config'),
    url(r'^profile/config/(\w+)/$',      view.edit_config_option,                     name="profile_config_edit_option"),
    url(r'load_default_config/(\d)?/?$', view.load_default_config),

    # admin panel urls
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/doc$', get_redirect_function_to_url('/entelib/admin/doc/')),
    (r'^admin/', include(admin.site.urls)),
    (r'^admin$', get_redirect_function_to_url('/entelib/admin/')),

    url(r'howto/', view.howto, name='howto'),
    url(r'feedback/', view.feedback, name='feedback'),
    url(r'changelog/', view.changelog, name='changelog'),

    # default matcher
    (r'^$', view.default),
)
