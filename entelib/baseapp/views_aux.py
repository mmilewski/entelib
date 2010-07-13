# -*- coding: utf-8 -*-

from entelib.baseapp.models import Reservation, Rental, BookCopy, Book, User, Location
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date, datetime, timedelta
from config import Config
from django.db.models import Q
from entelib import settings
import baseapp.emails as mail
from baseapp.exceptions import *

config = Config()
today = date.today
now = datetime.now


def render_response(request, template, context={}):
    user = request.user
    context.update( {'go_back_link' : '<a href="javascript: history.go(-1)">Back</a>',
                     'can_access_admin_panel' : user.is_staff or user.is_superuser,
                     })
    # as far as we use perms with following convention, we can pass perms to templates easily:
    # if in-code perm's name is list_book, then template gets can_list_books variable
    baseapp_perms = ['list_books', 'add_bookrequest', 'list_bookrequests', 'view_own_profile', 'list_users', 'list_reports', 'list_cost_centers',
                     'list_emaillog', 'list_config_options',]
    for perm_name in baseapp_perms:
        perm_fullname = 'can_' + perm_name
        if user.has_perm('baseapp.' + perm_name):
            context[perm_fullname] = True
        else:
            context.pop(perm_fullname, None)

    # special cases
    if config.get_bool('is_cost_center_visible_to_anyone') == True:
        context['can_list_cost_centers'] = True


    for key, value in context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request)
    )


def render_forbidden(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_URL)
    return render_response(request, 'forbidden.html')


def render_not_implemented(request):
    return render_response(request, 'not_implemented.html')


def render_not_found(request, **kwargs):
    context = kwargs
    return render_response(request, 'not_found.html', context)


def filter_query(class_name, Q_none, Q_all, constraints):
    '''
    Desc:
        Applies many filters on class' object list. A filter may require all or any of it's conditions to be met.

    Args:
        class_name - the class we want to retrieve objects of
        Q_none - Q object that matches no object of class_name. E.g. class_name(id__exact='-1').
        Q_all - Q object that matches every object of class_name. E.g. class_name(id__contains='')
        constraints - list of 3-tuples in form of (keywords, any, Q_fun) where
            keywords - a list of keywords in unicode
            any - boolean indicating whether filter needs to match any or all keywords. True means any keyword, False means all of them
            Q_fun - function taking a unicode string and returning Q object. E.g. "lambda x: Q(some_field__icontains=x)"

    Return:
        [class_name] - list of class_name objects matching all predicates
    '''

    result = class_name.objects.all()
    for (keywords, any, Q_fun) in constraints:
        if not keywords:   # this check is needed for situation when any==True and keywords==[]. Then
            continue       # reduce below would return Q_none and finally empty result would be returned.
        if any:
            result = result.filter(reduce(lambda q,y: q | Q_fun(y), keywords, Q_none))
        else:
            #result = result.filter(reduce(lambda q,x: q & Q_fun(x), keywords, Q_all))
            for keyword in keywords:  # this should deal with filtering objects which has e.g. many authors
                result = result.filter(Q_fun(keyword))
    return result.distinct()


def get_book_details(book_copy):
    '''
    Desc:
        Returns a dictionary to be passed to some bookcopy template
    Args:
        book_copy - BookCopy object, of which we want to get details.
    Return:
        Dictionary describing book copy
    '''
    book_desc = {
        'title'          : book_copy.book.title,
        'shelf_mark'     : book_copy.shelf_mark,
        'authors'        : [a.name for a in book_copy.book.author.all()],
        'location'       : unicode(book_copy.location),
        'state'          : unicode(book_copy.state) + '. ' + ("Available for %d days." % book_copy_status(book_copy)) if is_book_copy_rentable(book_copy) \
                                                                                                                     else book_copy_status(book_copy),
        'publisher'      : unicode(book_copy.publisher),
        'year'           : book_copy.year,
        'cost_center'    : unicode(book_copy.cost_center),
        'publication_nr' : book_copy.publication_nr,
        'desc'           : book_copy.description,
        'desc_url'       : book_copy.description_url,
        'toc'            : book_copy.toc,
        'toc_url'        : book_copy.toc_url,
        'picture'        : book_copy.picture,
    }
    return book_desc


def get_locations_for_book(book_id):
    '''
    Desc:
        Result contains location L iff exists copy of book (book, which id is book_id) assigned to L.
    Return:
        List of instances of Location.
    '''
    try:
        b = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        print 'get_locations_for_book(%d): book not found' % book_id
        return []
    copies = b.bookcopy_set.only('location').all()
    return [ loc for loc in Location.objects.filter(id__in=[c.location.id for c in copies])]


def get_phones_for_user(user):
    '''
    Desc:
        Returns list of dicts {type, value} where type & value are string from Phone model

    Args:
        user -- instance of User class. NOT an id.
    '''
    return [ {'type':p.type.name, 'value':p.value} for p in user.get_profile().phone.all() ]


def is_reservation_rentable(reservation):
    '''
    Desc:
        Returns non zero integer or non empty string (which evaluates to True) if a reserved book can be rented; False otherwise
    '''
    status = reservation_status(reservation)
    if isinstance(status, int) and status >= 0:
        return True
    else:
        return False


def is_reservation_active(r):
    if r.when_cancelled == None and r.rental == None and r.end_date <= today():
        return True
    else:
        return False


# Q object filtering Reservation objects to be only active (available for renting) (maybe after few days)
Q_reservation_active = Q(when_cancelled=None) & Q(rental=None) & Q(end_date__gte=today())


def reservation_status(reservation):
    '''
    Desc:
        returns reservation status:
            integer means for how many days book can be rented
            string is explaining why rental is not possible
    '''
    all = Reservation.objects.filter(book_copy=reservation.book_copy).filter(rental=None).filter(when_cancelled=None).filter(end_date__gte=today())
    if reservation not in all:
        return 'Incorrect reservation'
    # ksiazka wypozyczona:
    if Rental.objects.filter(reservation__book_copy=reservation.book_copy).filter(end_date=None).count() > 0:
        return 'This copy is currently rented.'
    # ksiazka niedostepna
    if reservation.book_copy.state.is_available == False:
        return 'This copy is currently not available (' + reservation.book_copy.state.name + ').'
    # rezerwacja jest do przodu i sa jakies inne po drodze:
    if reservation.start_date > today() and all.filter(start_date__lt=reservation.start_date).count() > 0:
        return 'There are reservations before this one starts.'
    # jakas starsza jest aktywna
    if all.filter(id__lt=reservation.id).filter(start_date__lte=today()).filter(Q_reservation_active).count() > 0:  # WARNING: this might need modification if additional conditions are added to definition of active reservation
        return 'Reservation not first'
    max_allowed = config.get_int('rental_duration')
    try:
        max_possible = (min([r.start_date for r in all.filter(id__lt=reservation.id).filter(start_date__gt=today())]) - today()).days
    except ValueError:
        max_possible = max_allowed
    return min(max_allowed, max_possible)


def is_book_copy_rentable(book_copy):
    status = book_copy_status(book_copy)
    if isinstance(status ,int) and status >= 0:
        return True
    else:
        return False


def book_copy_status(book_copy):
    '''
    Desc:
        Returns book copy status.

    Arg:
        book_copy is BookCopy object.

    Returns:
        integer n mean's rentable for n days. String explains why not rentable.
    '''
    if book_copy.state.is_available == False:
        return  u'Unavailable'
    elif Rental.objects.filter(reservation__book_copy=book_copy).filter(end_date__isnull=True).count() > 0:
        return  u'Rented'
    elif Reservation.objects.filter(book_copy=book_copy).filter(start_date__lte=today()).filter(end_date__gt=today()).filter(when_cancelled=None).filter(rental=None).count() > 0:
        return u'Reserved'

    max_allowed = config.get_int('rental_duration')
    try:
        max_possible = (min([r.start_date for r in
            Reservation.objects.filter(book_copy=book_copy).filter(end_date__gt=today()).filter(when_cancelled=None).filter(rental=None)]) - today()).days
        if max_possible < 0:
            max_possible = 0
    except ValueError:
        max_possible = max_allowed
    return min(max_allowed, max_possible)


def rent(reservation, librarian):
    rentable = is_reservation_rentable(reservation) and librarian.has_perm('baseapp.add_rental')
    if rentable:
        rental = Rental(reservation=reservation, who_handed_out=librarian, start_date=datetime.now())
        rental.save()
        mail.made_rental(rental)
        return True
    else:
        return False


def mark_available(book_copy):
    reservations = Reservation.objects.filter(rental=None).filter(start_date__lte=date.today)  # TODO tylko aktywne? jak rozwiazac sytuacje, jak ktos zarezerwowal od jutra?
    if reservations.count() > 0:
        reservations[0].active_since = today()
        # TODO notify user he can rent the book


def cancel_reservation(reservation, user):
    if reservation.for_whom != user and not user.has_perm("baseapp.change_reservation") or\
     user == reservation.for_whom and not user.has_perm("baseapp.change_own_reservation"):
            raise CancelReservationError("Not permitted")

    reservation.who_cancelled = user
    reservation.when_cancelled = now()
    reservation.save()

    return True


def cancel_all_user_resevations(librarian, user):
    '''
    Desc:
        all active user's resrvations are cancelled by librarian (which might be the same as user)
    '''
    try:
        for r in Reservation.objects.filter(for_whom=user).filter(Q_reservation_active):
            cancel_reservation(r, librarian)
    except CancelReservationError:
        pass  # TODO moze jeszcze cos sie przyda?

    return True


def non_standard_username(user_id):
    '''
    Return unicode string containing users first and last name if user_id is correct, None otherwise.
    '''
    try:
        u = User.objects.get(id=user_id)
        return u.first_name + ' ' + u.last_name
    except:
        return None


def when_copy_reserved(book_copy):
    config = Config()

    last_date = today() + timedelta(config.get_int('when_reserved_period'))
    if book_copy.state.is_available == False:
        return [{'from': today(), 'to': last_date}]

    reservations = Reservation.objects.filter(book_copy=book_copy).filter(Q_reservation_active).filter(start_date__lte=today() + timedelta(config.get_int('when_reserved_period')))
    active_rentals = Rental.objects.filter(reservation__book_copy=book_copy).filter(end_date__isnull=True)

    list = [(r.start_date, r.end_date) for r in reservations]
    if active_rentals:
        active_rental = active_rentals[0]
        list.append((today(), active_rental.reservation.end_date))

    list.sort()
    new_list = []

    if not list:
        return new_list

    lasta = list[0][0]
    lastb = list[0][1]
    if lastb > last_date:
        lastb = last_date

    for (a, b) in list[1:]:
        if a > lastb:
            new_list.append((lasta, lastb))
            lasta = a
            lastb = b
            if lastb > last_date:
                lastb = last_date
        else:
            lastb = max(b, lastb)
            if lastb > last_date:
                lastb = last_date

    if not new_list:
        new_list.append((lasta, lastb))
    else:
        if new_list[-1][1] != lastb:
            new_list.append((lasta, lastb))

    return [{'from' : a, 'to' : b} for (a,b) in new_list]
