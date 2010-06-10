#-*- coding=utf-8 -*-

from entelib.baseapp.models import Reservation, Rental, BookCopy
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect  # TODO usunąć HttpResponse
from datetime import date, datetime, timedelta
from config import Config

config = Config()


def render_response(request, template, context={}):
    user = request.user
    context.update( {'go_back_link' : '<a href="javascript: history.go(-1)">Back</a>',
                     'can_access_admin_panel' : user.is_staff or user.is_superuser,
                     })
    baseapp_perms = ['list_books', 'view_own_profile', 'list_users', 'list_reports']
    for perm_name in baseapp_perms:
        perm_fullname = 'can_' + perm_name
        if user.has_perm('baseapp.' + perm_name):
            context[perm_fullname] = True
        else:
            context.pop(perm_fullname, None)

    for key, value in context.items():
        context[key] = callable(value) and value() or value
    return render_to_response(
        template,
        context,
        context_instance=RequestContext(request)
    )


def render_forbidden(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/entelib/login/')
    return render_response(request, 'forbidden.html')


def render_not_implemented(request):
    return render_to_response(request, 'not_implemented.html')


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
        'title' : book_copy.book.title,
        'shelf_mark' : book_copy.shelf_mark,
        'authors' : [a.name for a in book_copy.book.author.all()],
        'location' : book_copy.location.name,
        'state' : book_copy.state.name,
        'publisher' : book_copy.publisher.name,
        'year' : book_copy.year,
        'publication_nr' : book_copy.publication_nr,
        'desc' : book_copy.description,
        'desc_url' : book_copy.description_url,
        'toc' : book_copy.toc,
        'toc_url' : book_copy.toc_url,
        'picture' : book_copy.picture,
    }
    return book_desc


def is_reservation_rentable(reservation):
    '''
    Desc:
        Returns non zero integer or non empty string (which evaluates to True) if a reserved book can be rented; False otherwise
    '''
    status = reservation_status(reservation)
    if isinstance(status, int):
        return status if status != 0 else 'infinity'
    else:
        return False


def reservation_status(reservation):
    '''
    Desc:
        returns reservation status:
            0 means rental possible.
            any other value is string explaining why rental is not possible
    '''
    all = Reservation.objects.filter(book_copy=reservation.book_copy).filter(rental=None)
    all = all.filter(end_date=None).order_by('id')  # TODO: doczytać o order by: koszt i zdefiniowanie kolejności wpp
    if reservation not in all:
        return 'Incorrect reservation'
    to_return = []
    if reservation != all.filter(start_date__lte=date.today())[0]:
        to_return += ['Reservation not first.']
    if Rental.objects.filter(reservation__book_copy=reservation.book_copy).filter(end_date=None).count() > 0:
        to_return += ['This copy is currently rented.']
    if reservation.book_copy.state.is_available == False:
        to_return += ['This copy is currently not available (' + reservation.book_copy.state.name + ').']
    if reservation.start_date > date.today():
        to_return += ['Reservation active since ' + reservation.start_date.isoformat() + '.']
    if reservation.end_date is not None:
        to_return += ['Reservation already pursued']   # TODO nie wiem czy to dobre słowo...
    if to_return:
        return ' '.join(to_return)

    if reservation == all[0]:
        return 0
    older = all[:all.index(reservation)]
    if min([(r.start_date - date.today()).days for r in older]) == 0:  # TODO nie mam fajnego pomysłu na asercje. No dobra, nie chce mi się robić porządnych asercji.
        raise 'assert fail: in reservation status: egsists older valid reservation'
    return min([(r.start_date - date.today()).days for r in older])


def is_book_copy_rentable(book_copy):
    if book_copy_status(book_copy) == 0:
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
        0 mean's rentable. Any other string explains why not rentable.
    '''
    to_return = []
    if book_copy.state.is_available == False:
        to_return += ['This copy is currently not available.']
    if Rental.objects.filter(reservation__book_copy=book_copy).filter(end_date=None).count() > 0:
        to_return += ['This copy is currently rented.']
    if Reservation.objects.filter(book_copy=book_copy).filter(end_date=None).count() > 0:
        to_return += ['This copy is reserved.']

    if to_return:
        return ' '.join(to_return)
    return 0


def rent(reservation, librarian):
    rentable = is_reservation_rentable(reservation)
    if rentable:
        rental = Rental(reservation=reservation, who_handed_out=librarian, start_date=datetime.now())
        rental.save()
        max_duration = config.get_int('rental_duration')
        duration = max_duration if rentable == 'infinity' or isinstance(rentable,int) and max_duration <= rentable else rentable
        reservation.end_date = date.today() + timedelta(days=duration)
        reservation.save()


def mark_available(book_copy):
    reservations = Reservation.objects.filter(rental=None).filter(start_date__lte=date.today)  #TODO tylko aktywne? jak rozwiązać sytuację, jak ktoś zarezerwował od jutra?
    if reservations.count() > 0:
        reservations[0].active_since = date.today()
        #TODO notify user he can rent the book
