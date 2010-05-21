#-*- coding=utf-8 -*-

from entelib.baseapp.models import Reservation, Rental
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect  # TODO usunąć HttpResponse
from datetime import date, datetime


def render_response(request, template, dict={}):
    if request.user.has_perm('baseapp.list_users'):
        dict.update( { 'can_list_users' : 'True' } )
    return render_to_response(
        template,
        dict,
        context_instance=RequestContext(request)
    )


def render_forbidden(request):
    if request.user.is_authenticated():
        return HttpResponse("Forbidden")
    else:
        return HttpResponseRedirect('/entelib/login/')


    '''
    tak będzie docelowo:
        if not request.user.is_authenticated():
            return HttpResponseRedirect('/entelib/login/')
        return render_to_response(
           'forbidden.html',
           {},
           context_instance=RequestContext(request)
        )
    '''


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
        if any:
            result = result.filter(reduce(lambda q,y: q | Q_fun(y), keywords, Q_none))
        else:
            result = result.filter(reduce(lambda q,x: q & Q_fun(x), keywords, Q_all))
    return result.distinct()


def get_book_details(book_copy):
    '''
    Desc:
        Returns a dictionary to be passed to some bookcopy template

    Args:
        book - Book object
        book_copy - BookCopy objects such that book_copy.book == book

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
        'description' : book_copy.description,
        'desc_url' : book_copy.toc_url,
        'toc' : book_copy.toc,
        'picture' : book_copy.picture,
    }
    print 'url' + book_copy.toc_url
    return book_desc


def rental_possible(reservation):
    '''
    Desc:
        Returns True if a rental can be completed; False otherwise
    '''
    if reservation_status(reservation) == 0:
        return True
    else:
        return False


def reservation_status(reservation):
    '''
    Desc returns reservation status:
        0 means rental possible.
        any other value is string explaining why rental is not possible
    '''
    all = Reservation.objects.filter(book_copy=reservation.book_copy).filter(rental=None).filter(for_whom=reservation.for_whom)
    if reservation not in all:
        return 'Incorrect reservation'
    to_return = []
    if reservation != all[0]:
        to_return += ['Reservation not first.']
    if Rental.objects.filter(reservation__book_copy=reservation.book_copy).filter(end_date=None).count() > 0:
        to_return += ['This copy is currently rented.']
    if reservation.book_copy.state.is_available == False:
        to_return += ['This copy is currently not available.']
    if reservation.start_date > date.today():
        to_return += ['Reservation not yet active.']
    if reservation.end_date is not None:
        to_return += ['Reservation already pursued']   # TODO nie wiem czy to dobre słowo...
    if to_return:
        return ' '.join(to_return)
    return 0


def rent(reservation, librarian):
    if rental_possible(reservation):
        try:
            rental = Rental(reservation=reservation, who_handed_out=librarian, start_date=datetime.now())
            rental.save()
            reservation.end_date = date.today() + timedelta(days=dateConfig.get_int('max_rental_time'))
            reservation.save()
            return True
        except Exception:
            return 'error'
    return 'rental not possible'
