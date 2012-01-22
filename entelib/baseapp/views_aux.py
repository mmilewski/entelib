# -*- coding: utf-8 -*-
# TODO we need some consequence: either we write a full path in imports starting with entelib or we don't  - mbr
from entelib.baseapp.models import Reservation, Rental, BookCopy, Book, User, Location, TemporaryLocationMaintainer
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from datetime import date, datetime, timedelta
from config import Config
from django.db import transaction
from django.db.models import Q
from django.contrib import messages
from entelib import settings
from baseapp.exceptions import *
import baseapp.emails as mail
from django.db.models.aggregates import Min
import random
import utils

config = Config()
today = date.today
now = datetime.now


def is_on_leave(user):
    '''
    True if user added some temporary maintainers to any of his libraries.
    '''
    assert isinstance(user, User)
    return TemporaryLocationMaintainer.objects.filter(adder=user).count() > 0


def render_response(request, template, context={}):
    user = request.user
    if user.is_anonymous():
        return render_to_response(
            template,
            context,
            context_instance=RequestContext(request)
            )

    config = Config(user)
    application_ip = 8080
    context.update( {'go_back_link' : '<a href="javascript: history.go(-1)">Back</a>',
                     'can_access_admin_panel' : user.is_staff or user.is_superuser,
                     'display_tips' : config.get_bool('display_tips'),
                     'display_only_editable_config_options' : config.get_bool('display_only_editable_config_options'),
                     'unique_num' : random.randint(0,9999999999999),
                     'application_ip' : application_ip,
                     'application_url' : Config(request.user).get_str('application_url'),
                     'is_dev' : settings.IS_DEV,
                     'is_on_leave' : is_on_leave(request.user)
                     })
    # as far as we use perms with following convention, we can pass perms to templates easily:
    # if in-code perm's name is list_book, then template gets can_list_books variable
    baseapp_perms = ['list_books', 'add_bookrequest', 'list_bookrequests', 'view_own_profile',
                     'list_users', 'list_reports', 'list_emaillog',
                     'list_config_options', 'load_default_config', 'edit_option',
                     'list_locations', 'view_location',
                     ]
    for perm_name in baseapp_perms:
        perm_fullname = 'can_' + perm_name
        if user.has_perm('baseapp.' + perm_name):
            context[perm_fullname] = True
        else:
            context.pop(perm_fullname, None)

    # special cases
    context['can_display_costcenter'] = config.get_bool('is_cost_center_visible_to_anyone') or user.has_perm('baseapp.list_costcenters')


    for key, value in context.items():
        context[key] = value() if callable(value) else value
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request)
    )


def render_forbidden(request, msg=''):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_URL)
    context = {'msg' : msg}
    return render_response(request, 'forbidden.html', context)


def render_not_implemented(request):
    return render_response(request, 'not_implemented.html')


def render_not_found(request, **kwargs):
    '''
    Args:
        msg        -- displays msg.
        item_name  -- displays: item_name not found.
    '''
    context = kwargs
    return render_response(request, 'not_found.html', context)


def filter_query(class_name, Q_none, constraints):
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
        [objects] - list of class_name objects matching all predicates
    '''

    result = class_name.objects.all()
    for (keywords, any, Q_fun) in constraints:
        if not keywords:   # this check is needed for situation when any==True and keywords==[]. Then
            continue       # reduce below would return Q_none and finally empty result would be returned.
        if any:
            result = result.filter(reduce(lambda q,y: q | Q_fun(y), keywords, Q_none))
        else:
            for keyword in keywords:  # this should deal with filtering objects which have e.g. many authors
                result = result.filter(Q_fun(keyword))
    return result.distinct()

def get_users_details_list(first_name, last_name, username, email, building_id, active_only=False, inactive_only=False, awaiting_activation_only=False):
    '''
    Args:
        building_id is an int,
        other args are strings

    Return:
        list of dicts of user satisfying given criteria
    '''
    building_filter = Q()
    if building_id:
        building_filter = Q(userprofile__building__id=building_id)

    users = User.objects.select_related('userprofile')

    if inactive_only:
        users = users.filter(is_active=False)
    if active_only:
        users = users.filter(is_active=True)
    if awaiting_activation_only:
        users = users.filter(userprofile__awaits_activation=True)

    user_details =    [ {'username'   : u.username,
                         'last_name'  : u.last_name,
                         'first_name' : u.first_name,
                         'email'      : u.email,
                         'userprofile': u.userprofile,
                         # 'url'        : "%d/" % u.id,  # relative path to user profile
                         'id'         : u.id,
                         }      for u in users.filter(first_name__icontains=first_name)
                                              .filter(last_name__icontains=last_name)
                                              .filter(username__icontains=username)
                                              .filter(email__icontains=email)
                                              .filter(building_filter)
            ]
    return user_details


def get_book_details(book_copy):
    '''
    Desc:
        Returns a dictionary to be passed to some bookcopy template
    Args:
        book_copy - BookCopy object, of which we want to get details.
    Return:
        Dictionary describing book copy
    '''
    status = book_copy_status(book_copy)
    copy_state = ("Available for %d days." % status.rental_possible_for_days()) if status.is_available() else status.why_not_available()
    location_url_pattern = '/entelib/locations/%d/'
    book_desc = {
        'id'             : book_copy.id,
        'book'           : book_copy.book,
        'title'          : book_copy.book.title,
        'shelf_mark'     : book_copy.shelf_mark,
        'authors'        : [a.name for a in book_copy.book.author.all()],
        'location'       : book_copy.location,
        'location_str'   : unicode(book_copy.location),
        'location_url'   : (location_url_pattern % book_copy.location.id) if book_copy.location else None,
        'state'          : copy_state,
        'publisher'      : book_copy.publisher,
        'publisher_str'  : unicode(book_copy.publisher),
        'year'           : book_copy.year,
        'cost_center'    : book_copy.cost_center,
        'cost_center_str': unicode(book_copy.cost_center),
        'publication_nr' : book_copy.publication_nr,
        'desc'           : book_copy.description,
        'desc_url'       : book_copy.description_url,
        'toc'            : book_copy.toc,
        'toc_url'        : book_copy.toc_url,
    }
    return book_desc


class CannotManageMaintainers(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


def add_temporary_maintainer_for_location(tmplocation, maintainer, who_adds):
    '''
    Desc:
        Add temporary maintainer for location. First, chceks if one can do that (is 'real' maintainer of location).
    Args:
        tmplocation - instance of Location
        maintainer - instance of User
        who_adds - instance of User, who adds temporary maintainer
    '''
    assert isinstance(tmplocation, TemporaryLocationMaintainer)
    assert isinstance(maintainer, User)
    assert isinstance(who_adds, User)

    # check
    adder_locations = Location.objects.filter(maintainer=who_adds)
    if tmplocation.location not in adder_locations:
        raise CannotManageMaintainers('Forbidden to add maintainers: not location maintainer')

    # add
    record = tmplocation
    record.maintainer.add(maintainer)
    record.save()


def remove_temporary_maintainer_from_location(tmplocation, maintainer, who_removes):
    '''
    Desc:
        Removes maintainer from location. First, checks if one can do that (is 'real' maintainer of location).
    Args:
        tmplocation - instance of TemporaryLocationMaintainer
        maintainer - instance of User, which will be removed from location
        who_removes - instance of User, which removes maintainer from location
    '''
    assert isinstance(tmplocation, TemporaryLocationMaintainer)
    assert isinstance(maintainer, User)
    assert isinstance(who_removes, User)
    # check
    remover_locations = Location.objects.filter(maintainer=who_removes)
    if tmplocation.location not in remover_locations:
        raise CannotManageMaintainers('Forbidden to remove maintainers: not location maintainer')

    # remove
    tmplocation.maintainer.remove(maintainer)


def get_maintainers_description_for_location(location):
    '''
    Desc:
        Return list of maintainers for given location, this is 'real' maintainers  + temporary maintainers
    Args:
        location - instance of Location
    Return:
        list of dicts {user, temporary}. user - User instance, temporary - bool (does maintainer do sb's else duties)
    '''
    if not (isinstance(location, Location)):
        assert location is Location
    mts = [ {'user': u, 'temporary': False} for u in location.maintainer.all() ]
    tmplocs = TemporaryLocationMaintainer.objects.filter(location=location)
    for tmploc in tmplocs:
        for u in tmploc.maintainer.all():
            ud = {'user': u, 'temporary': True}
            if ud not in mts:
                mts.append(ud)
    return mts


def get_maintainers_for_location(location):
    '''
    Desc:
        Almost same as get_maintainers_description_for_location, but returns list of Users
    Return:
        List of User instances, who maintain given location.
    '''
    return [ d['user'] for d in get_maintainers_description_for_location(location) ]


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
        Returns True if a reserved book can be rented; False otherwise
    '''
    status = reservation_status(reservation)
    if isinstance(status, int) and status >= 0:
        return True
    else:
        return False


# Q object filtering Reservation objects to be only active (which means not rented or cancelled or expired)
Q_reservation_active = Q(when_cancelled=None) & Q(rental=None) & Q(end_date__gte=utils.today())


def reservation_status(reservation):
    '''
    Desc:
        returns reservation status:
            integer means for how many days book can be rented
            string is explaining why rental is not possible
    '''
    all = Reservation.objects.filter(book_copy=reservation.book_copy)\
                             .filter(rental=None)\
                             .filter(when_cancelled=None)\
                             .filter(end_date__gte=utils.today())
    if reservation not in all:
        return 'Incorrect reservation'
    # book rented:
    if Rental.objects.filter(reservation__book_copy=reservation.book_copy).filter(end_date=None).count() > 0:
        return 'Copy rented.'
    # book unavailable:
    if reservation.book_copy.state.is_available == False:
        return 'Copy not available (' + reservation.book_copy.state.name + ').'
    # too early
    if reservation.start_date > utils.today():
        return 'Reservation is not yet active'
    # reservation cannot be purchased for there are some reservation before this one starts
    if reservation.start_date > utils.today() and all.filter(start_date__lt=reservation.start_date).count() > 0:
        return 'There are reservations before this one starts.'
    # some older reservation is active
    if all.filter(id__lt=reservation.id).filter(start_date__lte=utils.today()).filter(Q_reservation_active).count() > 0:
        # WARNING/NOTE: this might need modification if additional conditions are added to definition of active reservation
        return 'Reservation in queue'
    max_allowed = config.get_int('rental_duration')
    try:
        max_possible = (min([r.start_date for r in all.filter(id__lt=reservation.id).filter(start_date__gt=utils.today())]) - utils.today()).days
    except ValueError:
        max_possible = max_allowed
    return min(max_allowed, max_possible)


def cancel_reservation(reservation, canceller):
    '''
    Desc:
        Cancels reservation.
    Arg:
        reservation - instance of Reservation. Reservation to be cancelled.
        canceller - instance of User. User who cancels the reservation.
    '''
    assert isinstance(reservation, Reservation)
    assert isinstance(canceller, User)
    reservation.when_cancelled = now()
    reservation.who_cancelled = request.user
    reservation.save()


def is_book_copy_rentable(book_copy):
    return book_copy_status(book_copy).is_available()


class BookCopyStatus(object):
    def __init__(self, available, nr_of_days=0, explanation=u''):
        self.available = available
        self.nr_of_days = nr_of_days
        self.explanation = explanation

    def is_available(self):
        return self.available

    def why_not_available(self):
        if self.is_available():
            return False
            # raise ValueError('BookCopyStatus.why_not_available error: available')
        return self.explanation

    def rental_possible_for_days(self):
        if not self.is_available():
            raise ValueError('BookCopyStatus.rental_possible_for error: rental not possible.')
        else:
            return self.nr_of_days

    def set(self, available=None, nr_of_days=None, explanation=None):
        if available is not None:
            self.available = available
        if nr_of_days is not None:
            self.nr_of_days = nr_of_days
        if explanation is not None:
            self.explanation = explanation
        return self

    def __unicode__(self):
        if self.is_available():
            return u'Available'
        return self.explanation


def book_copy_status(book_copy):
    '''
    Desc:
        Returns book copy status object.

    Arg:
        book_copy is BookCopy object.

    Returns:
        BookCopyStatus object
    '''
    statuses = book_copies_status([book_copy])
    copy_id, status = statuses.items()[0]
    return status['status']


def get_active_rentals_for_copies(copies_ids, only=[], related=[]):
    '''
    Collects and returns list of Rental objects for specified book copies.

    Args:
        copies_ids -- ids of copies for which you want to get rentals.
        only -- fields one need to use. List of strings. As default 'reservation__book_copy__id' is used.
        related -- related fields/objects. As default 'reservation__book_copy' is used.
    '''
    only_fields = only + ['reservation__book_copy__id']
    related_fields = related + ['reservation__book_copy']
    rentals = Rental.objects.only(*only_fields) \
                            .select_related(*related_fields) \
                            .filter(reservation__book_copy__id__in=copies_ids) \
                            .filter(end_date__isnull=True)
    return rentals


def get_reservations_for_copies(copies_ids, only=[], related=[]):
    '''
    Collects and returns list of Reservation objects for given book copies.

    Args:
        copies_ids -- ids of copies for which you want to get reservations. List of ints.
        only -- model fields one need to use. List of strings. As default 'book_copy__id' is used.
    '''
    only_fields = only + ['book_copy__id']
    reservations = Reservation.objects.only(*only_fields) \
                                      .filter(book_copy__id__in=copies_ids) \
                                      .filter(start_date__lte=utils.today()) \
                                      .filter(Q_reservation_active)
    return reservations


def book_copies_status(copies):
    '''
    Desc:
        Returns statuses of given copies.

    Args:
        copies -- list of BookCopy instances

    Returns:
        dict like { copy_id : {'copy' : given_copy_instance,
                               'status' : BookCopyStatus instance
                              },
                    ...
                  }
    '''
    copies_ids = [ c.id for c in copies ]

    result = {}
    for kopy in copies:
        result[kopy.id] = {}
        result[kopy.id]['copy'] = kopy
        result[kopy.id]['status'] = None
        if not kopy.state.is_available:
            result[kopy.id]['status'] = BookCopyStatus(available=False, explanation=u'Unavailable: ' + kopy.state.name)

    # find rented copies
    rentals = get_active_rentals_for_copies(copies_ids)
    for rental in rentals:
        copy_id = rental.reservation.book_copy.id
        if not result[copy_id]['status']:
            user = rental.reservation.for_whom
            result[copy_id]['status'] = BookCopyStatus(available=False,
                    explanation=u'Rented until {0} by {1}'.format(
                                        rental.reservation.end_date.isoformat(),
                                                    u'<a href="mailto:{0}">{0}</a>'.format(user.email)))

    # find reserved copies, that can already be rented
    reservations = get_reservations_for_copies(copies_ids)
    for reservation in reservations:
        copy_id = reservation.book_copy.id
        if not result[copy_id]['status']:
            result[copy_id]['status'] = BookCopyStatus(available=False, explanation=u'Reserved')

    # finds first (in sense of timeline) reservation for each copy.
    rsvs = Reservation.objects.filter(book_copy__id__in=copies_ids)\
                              .filter(Q_reservation_active)\
                              .values('book_copy__id')\
                              .annotate(min_start_date=Min('start_date'))

    # update statuses for copies unstatused in code above -- copies are rentable, but we don't know for how long, yet.
    # rsvs contains information about nearest (but in future) reservation.
    max_allowed = config.get_int('rental_duration')
    for rsv in rsvs:
        copy = rsv['book_copy__id']
        if result[copy]['status']:
            continue
        try:
            min_start_date = rsv['min_start_date']
            max_possible = (min_start_date - utils.today()).days - 1
            if max_possible < 0:
                raise EntelibError('book_copy_status error: copy reserved') # this should not happen since all active reservations should already have status
        except ValueError:
            max_possible = max_allowed
        result[copy]['status'] = BookCopyStatus(available=True, nr_of_days=min(max_allowed, max_possible))

    for key in result.keys():
        if not result[key]['status']:
            result[key]['status'] = BookCopyStatus(available=True, nr_of_days=max_allowed)

    return result


def nr_of_available_copies(book):
    '''
    Arg: Book object.
    Return: nr of available copies of a book.

    WARNING: this is SLOW for it needs to touch every sigle copy and reservation
    '''
    copies = book_copies_status(book.bookcopy_set.all())
    counter = 0
    for id in copies:
        if copies[id]['status'].is_available():
            counter += 1
    return counter


def request_shipment(reservation):
    if not reservation.for_whom.userprofile.building:
        return False
    reservation.shipment_requested = True
    reservation.save()
    mail.shipment_requested(reservation)
    return True


def confirm_reservation(reservation):
    '''
    Check if reservation can be immediately rented and send appropriate email.
    '''
    preceding_reservations = Reservation.objects.filter(Q_reservation_active|Q(rental__isnull=False, rental__end_date__isnull=True), book_copy=reservation.book_copy, id__lt=reservation.id)
    if not preceding_reservations and reservation.start_date <= utils.today():
        mail.reservation_active(reservation)
        reservation.active_since = utils.today()
        reservation.save()
    else:
        mail.made_reservation(reservation)


def rent(reservation, librarian):
    '''
    Desc:
        Librarian rents book indicated by reservation. Return value says when it is supposed to be returned
    '''
    if not librarian.has_perm('baseapp.add_rental'):
        raise PermissionDenied
    if not librarian in reservation.book_copy.location.get_all_maintainers():
        raise PermissionDenied('One can only rent from location one maintains')
    if not is_reservation_rentable(reservation):
        raise PermissionDenied('Reservation not rentable.')
    max_end_date = utils.today() + timedelta(reservation_status(reservation)-1) # return one day before it's reserved
    if max_end_date < reservation.end_date:
        reservation.end_date = max_end_date
        reservation.save()
    rental = Rental(reservation=reservation, who_handed_out=librarian, start_date=datetime.now())
    rental.save()
    mail.made_rental(rental)
    return reservation.end_date


def return_rental(librarian, rental_id):
    '''
    Desc:
        librarian receives book from rental

    Args:
        librarian - User instance: accepts returnal
        rental_id - id of rental being ended
    '''
    returned_rental = get_object_or_404(Rental, id=rental_id)

    # not everyone can return book
    if not librarian.has_perm('baseapp.change_rental'):
        raise PermissionDenied
    if not librarian in returned_rental.reservation.book_copy.location.get_all_maintainers():
        raise PermissionDenied('One can only rent/return from location one maintains')

    # can't return a rental twice
    if returned_rental.end_date is not None:
        raise Rental.DoesNotExist('Rental already returned')

    # actual returning
    returned_rental.who_received = librarian
    returned_rental.end_date = datetime.now()
    returned_rental.save()
    mark_available(returned_rental.reservation.book_copy)   # someone might be waiting for that book


def max_prolongation_period(rental):
    '''
    Desc:
        Returnes number of days -- for how long book can be prolonged.
    Args:
        rental -- instance of Rental.
    '''
    assert isinstance(rental, Rental)
    reservation = rental.reservation

    days_left_to_enable_prolongation = Config().get_int('min_days_left_to_enable_prolongation')
    days_left_to_rend    = (reservation.end_date - utils.today()).days
    enabled_prolongation = days_left_to_rend <= days_left_to_enable_prolongation
    if not enabled_prolongation:
        return 0

    max_period = Config().get_int('max_prolongation_days')
    kopy       = reservation.book_copy
    for rsv in kopy.reservation_set.exclude(for_whom=reservation.for_whom):
        if rsv.start_date <= reservation.end_date < rsv.end_date:         # someone else reserved -> prolongation impossible
            return 0
        if reservation.end_date == rsv.start_date:
            return 0
        if rsv.end_date <= reservation.end_date:                          # other rsv finished -> no collision, continue processing
            continue
        if reservation.end_date < rsv.start_date:                         # other rsv starts in future -> try to shrink max_period
            max_period = min(max_period, (rsv.start_date - reservation.end_date).days - 1)
    return max_period


def send_prolongation_request(request, rental_id, requester):
    '''
    Desc:
        Sends prolongation request to librarians.
    Args:
        request -- http request - needed for messages
        rental_id -- uint
        requester -- instance of User,
    '''
    prol_logger = utils.get_logger('prolong')
    prol_logger.info("prolong_request()....")
    assert isinstance(rental_id, int)
    assert isinstance(requester, User)
    try:
        r = Rental.objects.get(pk=rental_id, reservation__for_whom=requester.id)
        max_period = max_prolongation_period(r)
        prol_logger.info("prolong_request() preconditions valid, ;; rental %d ;; found ." % rental_id)
        if max_period < 1:
            prol_logger.error("prolong_request() cannot prolong -- someone else reserved/prolonged or too early.")
            messages.error(request, "You CANNOT prolong this rental -- probably someone else reserved it or it is too early for prolongation.")
        else:
            prol_logger.info("prolong_request() request sent successfully.")
            mail.request_prolongation(requester=requester, rental=r)
            messages.info(request, "Request was sent to librarians, please WAIT FOR APPROVAL. Prolongation possible for %d days." % max_period)
    except Rental.DoesNotExist:
        messages.error(request, "Rental not found, unable to request for prolong.")


def prolong_rental(request, rental_id, requester, prolongator):
    '''
    Desc:
        Prolongs rental if possible.
    Args:
        request
        rental_id
        requester -- User. Owner of reservation and rental (one who is in possesion of book)
        prolongator
    '''
    prol_logger = utils.get_logger('prolong')
    prol_logger.info("prolong_rental()....")

    assert isinstance(rental_id, int)
    assert isinstance(requester, User)
    assert isinstance(prolongator, User)
    r = None
    try:
        r = Rental.objects.get(pk=rental_id, reservation__for_whom=requester)
    except Rental.DoesNotExist:
        messages.error(request, "Rental wasn't found, unable to prolong.")
        return

    prol_logger.info("prolong_rental() preconditions valid, rental present.")

    days_left_to_enable_prolongation = Config().get_int('min_days_left_to_enable_prolongation')
    days_left_to_rend    = (r.reservation.end_date - utils.today()).days
    enabled_prolongation = days_left_to_rend <= days_left_to_enable_prolongation
    max_period           = max_prolongation_period(r)
    can_prolong          = enabled_prolongation and max_period > 0 and prolongator.has_perm('baseapp.change_rental')

    prol_logger.info("prolong_rental() "
                     + ";; rental_id %d "
                     + ";; days_left_to_enable_prolongation %d "
                     + ";; days_left_to_rend %d "
                     + ";; enabled_prolongation %d "
                     + ";; max_period %d "
                     + ";; can_prolong %d "
                     %
                     r.id,
                     days_left_to_enable_prolongation,
                     days_left_to_rend,
                     enabled_prolongation,
                     max_period,
                     can_prolong
                     )

    if prolongator not in r.reservation.book_copy.location.get_all_maintainers():
        prol_logger.error("prolong_rental() prolongator not a location maintainer.")
        messages.error(request, "You cannot prolong this book - it's not from location you maintain.")
        return
    if not enabled_prolongation:
        prol_logger.error("prolong_rental() prolongator not enabled.")
        messages.error(request, "It is TOO EARLY to prolong this rental: please wait for %d days." % (days_left_to_rend - days_left_to_enable_prolongation))
        return
    if max_period <= 0:
        prol_logger.error("prolong_rental() max_period less then zero.")
        messages.error(request, "Rental cannot be prolonged - probably someone reserved this book.")
        return
    if can_prolong:
        import datetime as dt
        old_end_date = r.reservation.end_date
        new_end_date = r.reservation.end_date + dt.timedelta(max_period)
        r.reservation.end_date = new_end_date
        r.reservation.save()
        prol_logger.info("prolong_rental() prolonged ;; rental_id %d "
                         + ";; old_end_date %s "
                         + ";; new_end_date %s "
                         %
                         r.id,
                         str(old_end_date),
                         str(new_end_date)
                         )

        mail.prolongated(r, prolongator, extra={'old_end_date': old_end_date,
                                                'new_end_date': new_end_date,
                                                    })
        messages.info(request, "Prolonged for %d days." % max_period)
    else:
        prol_logger.error("prolong_rental() you cannot prolong the rental.")
        messages.error(request, "You cannot prolong the rental.")


def show_user_rentals(request, user_id=False):
    '''
    Desc:
        Shows user's current rentals. Allows returning books.
    '''
    if not user_id:
        user = request.user
    else:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return render_not_found(request, item_name='User')

    post = request.POST  # a shorthand

    context = { 'first_name' : user.first_name,
                'last_name' : user.last_name,
                'email' : user.email,
                'reader' : user,
                }

    # Return button clicked for a rental:
    # but we care about it only if he is supposed to
    if request.user.has_perm('baseapp.change_rental') and\
       request.method == 'POST' and\
       'returned' in post:
        try:
            until_when = return_rental(librarian=request.user, rental_id=post['returned'])
            context['message'] = 'Successfully returned'
            messages.info(request, 'Successfully returned')
        except Rental.DoesNotExist:
            return render_not_found(request, item_name='Rental')
        except PermissionDenied:  # this might happen if user doesn't have 'change_rental' permission
            return render_forbidden

    # logger for prolongation
    prol_logger = utils.get_logger('prolong')

    # sending prolongation request to librarians
    if request.method == 'POST' and 'prolong_request' in post:
        rental_id = int(post['prolong_rental_id'])
        prol_logger.info("request ;; user %d %s ;; rental_id %d", user.id, user.get_full_name(), rental_id)
        send_prolongation_request(request, rental_id, user)

    # prolonging rental
    if request.method == 'POST' and 'prolong' in post and request.user.has_perm('baseapp.change_rental'):
        rental_id   = int(post['prolong_rental_id'])
        requester   = user
        prolongator = request.user
        prol_logger.info("prolonging ;; prolongator %d %s ;; requester %d %s ;; rental_id %d",
                         prolongator.id, prolongator.get_full_name(),
                         requester.id, requester.get_full_name(),
                         rental_id)
        prolong_rental(request, rental_id, requester, prolongator)

    # find user's rentals
    user_rentals = Rental.objects.filter(reservation__for_whom=user.id).filter(end_date__isnull=True)

    # and put them in a dict:
    days_left_to_enable_prolongation = Config().get_int('min_days_left_to_enable_prolongation')
    rent_list = []
    for r in user_rentals:
        max_period               = max_prolongation_period(r)
        days_left_to_rend        = (r.reservation.end_date - utils.today()).days
        enabled_prolongation     = days_left_to_rend <= days_left_to_enable_prolongation
        can_request_prolongation = enabled_prolongation and (request.user==r.reservation.for_whom)           # owner of reservation
        can_prolong              = enabled_prolongation \
                                    and max_period > 0 \
                                    and request.user.has_perm('baseapp.change_rental') \
                                    and (request.user in r.reservation.book_copy.location.get_all_maintainers())

        # msg('enabled_prolongation: %d' % enabled_prolongation)
        # msg('can_request_prolongation: %d' % can_request_prolongation)
        # msg('can_prolong: %d' % can_prolong)
        # msg('days_left_to_enable_prolongation: %d' % days_left_to_enable_prolongation)
        # msg('max_period: %d' % max_period)

        rent_list.append({
                'id'                         : r.id,
                'shelf_mark'                 : r.reservation.book_copy.shelf_mark,
                'title'                      : r.reservation.book_copy.book.title,
                'authors'                    : [a.name for a in r.reservation.book_copy.book.author.all()],
                'from_date'                  : r.start_date.date(),
                'to_date'                    : r.reservation.end_date,
                'returnable'                 : request.user in r.reservation.book_copy.location.get_all_maintainers(),
                'rental'                     : r,
                'can_request_prolongation'   : can_request_prolongation,
                'can_prolong'                : can_prolong,
                'prolongation_length'        : max_period,
                'cannot_request_nor_prolong' : not (can_request_prolongation or can_prolong),
                })

    # put rentals into context
    context['rows'] = rent_list

    # if user can change rentals then he can return books
    template = 'user_rentals_return_allowed.html' if request.user.has_perm('baseapp.change_rental') else 'user_rentals.html'

    return render_response(request, template, context)


def show_user_rental_archive(request, user_id=False):
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user

    rentals = Rental.objects.filter(reservation__for_whom=user)

    rent_list = []
    for rental in rentals:
        rent_list.append({
            'id'       : rental.reservation.book_copy.shelf_mark,
            'title'    : rental.reservation.book_copy.book.title,
            'authors'  : [a.name for a in rental.reservation.book_copy.book.author.all()],
            'rented'   : rental.start_date.date(),
            'returned' : rental.end_date.date() if rental.end_date else None,
            })

    context = { 'rows'     : rent_list,
                'for_whom' : user.first_name + ' ' + user.last_name if user_id else None,
                'reader'   : user,
              }
    return render_response(request, 'rental_archive.html', context)


def mark_available(book_copy):
    '''
    Desc:
        If there is an active reservation awaiting for this copy, let it know.
    '''
    reservations = Reservation.objects.filter(Q_reservation_active, book_copy=book_copy).filter(start_date__lte=utils.today())
    if reservations.count() > 0:  # TODO: this probably can be done more effectively
        first_reservation = reservations[0]
        first_reservation.active_since = utils.today()
        first_reservation.save()
        mail.reservation_active(first_reservation)


def show_user_reservations(request, user_id=False):
    if not user_id:
        user = request.user
    else:
        user = get_object_or_404(User, id=user_id)

    # prepare some data
    context = { 'first_name'     : user.first_name,
                'last_name'      : user.last_name,
                'email'          : user.email,
                'reader'         : user,
                'cancel_all_url' : 'cancel-all/',
                'can_cancel'     : request.user.has_perm('baseapp.change_reservation') \
                                   or (request.user == user \
                                       and user.has_perm('baseapp.change_own_reservation'))
                }

    if request.method == 'POST':
        post = request.POST
        # if user is allowed to rent books, and there is a request for a rental
        if 'rent' in post:
            try:
                reservation = Reservation.objects.get(id=post['rent'])
            except Reservation.DoesNotExist:
                return render_not_found(request, item_name='Reservation')
            # rent him reserved book
            until_when = rent(reservation, request.user)
            context.update({'message' : 'Successfully rented until ' + until_when.isoformat()})
            messages.info(request, 'Successfully rented until ' + until_when.isoformat())

        # if user is wants to cancel reservation:
        elif 'cancel' in post:
            try:
                reservation = Reservation.objects.get(id=post['cancel'])
            except Reservation.DoesNotExist:
                return render_not_found(request, item_name='Reservation')
            # cancel reservation
            cancel_reservation(reservation, request.user)
            context.update({'message' : 'Cancelled.'})  # TODO: maybe we want undo option for that
        elif 'send' in post:
            try:
                reservation = Reservation.objects.get(id=post['send'])
            except Reservation.DoesNotExist:
                return render_not_found(request, item_name='Reservation')
            if not request_shipment(reservation):
                messages.info(request, "Send-request couldn't be set. Maybe building is not set in userprofile?")

    # find user active reservations
    user_reservations = Reservation.objects.filter(for_whom=user)\
                                           .filter(Q_reservation_active)
    # prepare user reservations
    reservation_list = [ {'id' : r.id,
                          # 'url' : unicode(r.id) + u'/',
                          'book_copy_id' : r.book_copy.id,
                          'shelf_mark' : r.book_copy.shelf_mark,
                          'rental_impossible' : '' if is_reservation_rentable(r) and len(r.book_copy.location.get_all_maintainers()) > 0 else reservation_status(r),
                          'title' : r.book_copy.book.title,
                          'authors' : [a.name for a in r.book_copy.book.author.all()],
                          'from_date' : r.start_date,
                          'to_date' : r.end_date,
                          'location' : unicode(r.book_copy.location),
                          'can_rent' : request.user.has_perm('baseapp.add_rental') and \
                                       request.user in r.book_copy.location.get_all_maintainers(),
                          'shipment_requested' : r.shipment_requested,
                          'reservation' : r,
                         } for r in user_reservations]
    context.update({'rows' : reservation_list})

    return render_response(request, 'user_reservations.html', context)


def show_user_reservation_archive(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        user = request.user

    reservations = Reservation.objects.filter(for_whom=user)

    reservation_list = []
    for reservation in reservations:
        rented = None
        returned = None
        cancelled = None

        if reservation.rental_set.all():
            rented = reservation.rental_set.all()[0].start_date.date()
            if reservation.rental_set.all()[0].end_date:
                returned = reservation.rental_set.all()[0].end_date.date()

        if reservation.who_cancelled:
            cancelled = 'Cancelled %s (%s)' % (reservation.when_cancelled.date().isoformat(), reservation.who_cancelled.first_name +\
                                                                                       ' ' + \
                                                                                       reservation.who_cancelled.last_name)
        elif reservation.when_cancelled:
            cancelled = 'Expired %s' % reservation.end_date.isoformat()

        reservation_list.append({
            'id' : reservation.book_copy.shelf_mark,
            'title' : reservation.book_copy.book.title,
            'authors' : [a.name for a in reservation.book_copy.book.author.all()],
            'reserved' : reservation.start_date,
            'reservation_end' : reservation.end_date,
            'rented' : rented,
            'returned' : returned,
            'cancelled' : cancelled,
            })
    context = {'rows' : reservation_list,
               'for_whom' : user.first_name + ' ' + user.last_name if user_id else None,
               'reader' : user,
               }

    return render_response(request, 'reservation_archive.html', context)



def cancel_reservation(reservation, user):
    if reservation.for_whom != user and not user.has_perm("baseapp.change_reservation") or\
     user == reservation.for_whom and not user.has_perm("baseapp.change_own_reservation"):
            raise PermissionDenied
    if reservation.rental_set.count() > 0:
        raise PermissionDenied('The reservation has already been purchased!')

    reservation.who_cancelled = user
    reservation.when_cancelled = now()
    reservation.save()


def do_cancel_user_reservations(user, canceller):
    for r in Reservation.objects.filter(for_whom=user).filter(Q_reservation_active):
        cancel_reservation(r, canceller)


def cancel_all_user_reservations(request, user):
    """
    Desc:
        all user's reservations are cancelled by canceller (who might be user)
    """
    canceller = request.user

    post = request.POST
    if request.method == 'POST' and 'sure' in post and post['sure'] == 'true':
        do_cancel_user_reservations(canceller, user)
        post = request.POST

        return render_response(request, 'reservations_cancelled.html',
            { 'first_name' : user.first_name,
              'last_name'  : user.last_name,
              'email'      : user.email,
            })
    else:
        return render_response(request, 'cancel_reservations.html',
            { 'first_name' : user.first_name,
              'last_name'  : user.last_name,
              'email'      : user.email,
            })


def user_full_name(user_id, first_name_first=False):
    """
    Return unicode string containing users first and last name if user_id is correct, None otherwise.
    If user_id will be User instance, this function will work as expected.
    """
    if isinstance(user_id, User):
        u = user_id
    else:
        try:
            u = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    if not isinstance(u, User):
        return None

    if first_name_first:
        return u.first_name + ' ' + u.last_name
    else:
        return  u.last_name + ', ' + u.first_name  # default


'''
def when_copy_reserved(book_copy):
    """
    This is Adi's function. It is used with the timebar.
    Im not touching it for we are going to work with the time bar, and this may come useless anyway.
    """
    config = Config()

    last_date = utils.today() + timedelta(config.get_int('when_reserved_period'))
    if book_copy.state.is_available == False:
        return [{'from': utils.today(), 'to': last_date}]

    reservations = Reservation.objects.filter(book_copy=book_copy) \
                                      .filter(Q_reservation_active) \
                                      .filter(start_date__lte=utils.today() + timedelta(config.get_int('when_reserved_period')))
    active_rentals = Rental.objects.filter(reservation__book_copy=book_copy) \
                                   .filter(end_date__isnull=True)

    list = [(r.start_date, r.end_date) for r in reservations]
    if active_rentals:
        active_rental = active_rentals[0]
        list.append((utils.today(), active_rental.reservation.end_date))

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

    result_list = [{'from' : a, 'to' : b} for (a,b) in new_list]
    return result_list
'''


def can_edit_global_config(user):
    '''
    Returns True iff user can edit global values.

    Args:
        user -- instance of User
    '''
    return user.userprofile.is_admin()


def internal_post_send_possible(reservation):
    return 'True' if len(reservation.book_copy.location.get_all_maintainers()) > 0 else False


def show_reservations(request, shipment_requested=False, only_rentable=True, all_locations=False):
    if request.method == 'POST':
        post = request.POST
        reservation = get_object_or_404(Reservation, id=post['reservation_id'])
        if 'rent' in post:
            user = reservation.for_whom
            until = rent(reservation, request.user)
            messages.info(request, 'Rented %s (%s) to %s until %s.' % \
                (reservation.book_copy.book.title, reservation.book_copy.shelf_mark, user_full_name(reservation.for_whom), until.isoformat()))
        if 'cancel' in post:
            cancel_reservation(reservation, request.user)
            messages.info(request, 'Cancelled.')
    context = {}
    locations = request.user.location_set.all()  # locations maintained by user
    reservations = Reservation.objects.filter(Q_reservation_active)
    if shipment_requested:
        reservations = reservations.filter(shipment_requested=True).select_related()
    if not all_locations:
        reservations = reservations.filter(book_copy__location__in=locations)
    if only_rentable:
        reservations = [r for r in reservations.filter(start_date__lte=utils.today()) if is_reservation_rentable(r)]

    reservation_list = [
                        { 'id'                : r.id,
                          'user'              : user_full_name(r.for_whom.id),
                          'start_date'        : r.start_date,
                          'end_date'          : r.end_date,
                          'location'          : r.book_copy.location,
                          'shelf_mark'        : r.book_copy.shelf_mark,
                          'title'             : r.book_copy.book.title,
                          'authors'           : [a.name for a in r.book_copy.book.author.all()],
                          'rental_possible'   : is_reservation_rentable(r),
                        } for r in reservations ]
    context.update({ 'rows' : reservation_list })
    if shipment_requested:
        context.update({ 'header' : 'Shipment requests',
                         'shipments' : True, })
    elif not only_rentable:
        context.update({ 'header' : 'All active reservations',
                         'show_all' : True, })
    else:
        context.update({ 'header' : 'Current reservations'})
    return render_response(request, 'current_reservations.html', context)

@transaction.commit_on_success
def activate_user(admin, user):
    '''
    Activate user and notify him.
    '''
    if not admin.has_perm('auth.change_user'):
        raise PermissionDenied('You are not allowed to activate/deactivate users. Perm is "auth.change_user"')
    profile = user.userprofile
    profile.awaits_activation = False
    profile.save()
    user.is_active = True
    user.save()
    mail.user_activated(user)


@transaction.commit_on_success
def deactivate_user(admin, user):
    '''
    Deactivate user and notify him.
    '''
    if not admin.has_perm('auth.change_user'):
        raise PermissionDenied('You are not allowed to activate/deactivate users. Perm is "auth.change_user"')
    profile = user.userprofile
    profile.awaits_activation = False
    profile.save()
    user.is_active = False
    user.save()
    mail.user_deactivated(user, admin)


class ForgotPasswordHandler(object):
    def __init__(self, user):
        assert isinstance(user, User)
        self.user = user
        self.new_password = self.generate_new_password()

    def generate_new_password(self):
        '''
        Generates new password and returns it.
        '''
        from datetime import datetime
        from hashlib import md5
        value_to_hash = repr(datetime.now()) + self.user.email
        new_password = md5(value_to_hash).hexdigest()
        return new_password

    def reset_password(self, email_user=True):
        """
        Resets user's password. Sends email iff email_user is True.
        """
        user = self.user
        user.set_password(self.new_password)
        user.save()
        if email_user:
            mail.password_reset(self.user, self.new_password)

