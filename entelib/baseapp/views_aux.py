#-*- coding=utf-8 -*-

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect  # TODO usunąć HttpResponse
from datetime import date


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


def rental_possible(user, copy, reservation):
    '''
    Desc:
        Returns True if a rental can be completed.
        Warning: returns unicode if rental cannot be accomplished
    '''

    all = Reservation.objects.filter(book_copy=copy).filter(end_date=None)
    if reservation not in all:
        return 'Incorrect reservation'
    if reservation != all[0]:
        return 'Reservation not first'
    if reservation.start_date > date.today():
        return 'Reservation not yet active'
    if reservation.end_date is not None:
        return 'Reservation already pursued'   # TODO nie wiem czy to dobre słowo...
    if copy.state.is_available == False:
        return 'This copy is currently not available'
    return True
