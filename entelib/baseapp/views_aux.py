#-*- coding=utf-8 -*-

from entelib.baseapp.models import Reservation, Rental, BookCopy, Book, User
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date, datetime, timedelta
from config import Config
import csv

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


def generate_csv(report_type, from_date, to_date):
    '''
    Desc:
        Returns csv file in HTTP response.

    Args:
        report_type - type of the report
        from_date, to_date - describe the time period for the report

    Return:
        csv file in HTTP response.
    '''

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report.csv'
    writer = csv.writer(response)

    report_data = get_report_data(report_type, from_date, to_date)
    if report_data['error']:
        writer.writerow([u'Error - probably bad date format'.encode('utf8')])
        return response

    if report_type == u'status' or report_type == u'lost_books':
        writer.writerow([   u'Title'.encode('utf8'),
                            u'Shelf mark'.encode('utf8'),
                            u'Location'.encode('utf8'),
                            u'Status'.encode('utf8'),
                            u'Last time rented for'.encode('utf8'),
                            u'Last time rented on'.encode('utf8'),
                            u'Last time rented by'.encode('utf8')])
        books = report_data['report']
        for book in books:
            writer.writerow([   book['title'].encode('utf8'),
                                unicode(book['shelf_mark']).encode('utf8'),
                                book['location'].encode('utf8'),
                                book['status'].encode('utf8'),
                                book['for_whom'].encode('utf8'),
                                unicode(book['when']).encode('utf8'),
                                book['by_whom'].encode('utf8') ])

    elif report_type == u'most_often_rented':
        if from_date == u'' or to_date == u'':
            writer.writerow([u'Title'.encode('utf8'), u'Number of rentals'.encode('utf8')])
        else:
            writer.writerow([u'Title'.encode('utf8'), (u'Number of rentals from ' + from_date + u' to ' + to_date).encode('utf8')])
        books = report_data['report']
        for book in books:
            writer.writerow([ book['title'].encode('utf8'), unicode(book['num_of_rentals']).encode('utf8') ])

    elif report_type == u'most_often_reserved':
        if from_date == u'' or to_date == u'':
            writer.writerow([u'Title'.encode('utf8'), u'Number of reservations'.encode('utf8')])
        else:
            writer.writerow([u'Title'.encode('utf8'), (u'Number of reservations from ' + from_date + u' to ' + to_date).encode('utf8')])
        books = report_data['report']
        for book in books:
            writer.writerow([ book['title'].encode('utf8'), unicode(book['num_of_reservations']).encode('utf8') ])

    elif report_type == u'black_list':
        if from_date == u'' or to_date == u'':
            writer.writerow([u'Name'.encode('utf8'), u'Number of cancels'.encode('utf8')])
        else:
            writer.writerow([u'Name'.encode('utf8'), (u'Number of cancels from ' + from_date + u' to ' + to_date).encode('utf8')])
        users = report_data['report']
        for user in users:
            writer.writerow([ user['name'].encode('utf8'), unicode(user['num_of_cancels']).encode('utf8') ])

    return response


def get_report_data(report_type, from_date, to_date):
    '''
    Desc:
        Returns data for creating selected report.

    Args:
        report_type - type of the report
        from_date, to_date - describe the time period for the report

    Return:
        List describing the report, template name, info on encountered errors.
    '''

    if report_type == u'status':
        book_infos = []
        books = BookCopy.objects.all().order_by('book__title')
        last_rentals = {}
        rentals = Rental.objects.all()

        for rental in rentals:
            book_copy_id = rental.reservation.book_copy.id
            start_date = rental.start_date
            if book_copy_id not in last_rentals:
                last_rentals.update({book_copy_id: {  'when': start_date,
                                                    'for_whom': rental.reservation.for_whom.first_name + u' ' +
                                                                rental.reservation.for_whom.last_name,
                                                    'by_whom':  rental.who_handed_out.first_name + u' ' +
                                                                rental.who_handed_out.last_name}})
            elif last_rentals[book_copy_id]['when'] < start_date:
                last_rentals.update({book_copy_id: {  'when': start_date,
                                                    'for_whom': rental.reservation.for_whom.first_name + u' ' +
                                                                rental.reservation.for_whom.last_name,
                                                    'by_whom':  rental.who_handed_out.first_name + u' ' +
                                                                rental.who_handed_out.last_name}})

        for book in books:
            book_details = get_book_details(book)
            if book.id not in last_rentals:
                not_rented_yet = True
            else:
                not_rented_yet = False

            if not_rented_yet:
                for_whom = when = by_whom = u'Not rented yet'
            else:
                last_rental = last_rentals[book.id]
                (for_whom, when, by_whom) = (last_rental['for_whom'], last_rental['when'].date(), last_rental['by_whom'])

            title = book_details['title']
            shelf_mark = book_details['shelf_mark']
            location = book_details['location']

            status = book_copy_status(book)
            if not status:
                status = u'Rentable'

            book_infos.append({ 'title': title,
                                'shelf_mark': shelf_mark,
                                'location': location,
                                'status': status,
                                'for_whom': for_whom,
                                'when': when,
                                'by_whom': by_whom,
                                'not_rented_yet': not_rented_yet})

        return {'report': book_infos, 'template': 'library_status.html', 'error': False}

    ###

    elif report_type == u'most_often_rented':
        book_infos = []
        books = Book.objects.all()
        rentals = Rental.objects.all()
        date_empty = False
        nums_of_rentals = {}

        if from_date == u'' or to_date == u'':
            date_empty = True
        else:
            try:
                [y, m, d] = map(int,from_date.split('-'))
                start_date = date(y, m, d)
                [y, m, d] = map(int,to_date.split('-'))
                end_date = date(y, m, d)
            except:
                return {'error': True, 'report': [], 'template': 'reports.html'}

        for book in books:
            if book.id not in nums_of_rentals:
                nums_of_rentals.update({book.id: 0})

        for rental in rentals:
            book_id = rental.reservation.book_copy.book.id
            if date_empty:
                nums_of_rentals[book_id] += 1
            else:
                if rental.start_date.date() >= start_date and rental.start_date.date() <= end_date:
                    nums_of_rentals[book_id] += 1

        for book in books:
            book_infos.append({'title': book.title, 'num_of_rentals': nums_of_rentals[book.id]})

        return {'report': sorted(book_infos, key=lambda k: k['num_of_rentals'], reverse=True), 'template': 'most_often_rented.html', 'error': False}

    ###

    elif report_type == u'most_often_reserved':
        book_infos = []
        books = Book.objects.all()
        reservations = Reservation.objects.all()
        nums_of_reservations = {}
        date_empty = False

        if from_date == u'' or to_date == u'':
            date_empty = True
        else:
            try:
                [y, m, d] = map(int,from_date.split('-'))
                start_date = date(y, m, d)
                [y, m, d] = map(int,to_date.split('-'))
                end_date = date(y, m, d)
            except:
                return {'error': True, 'report': [], 'template': 'reports.html'}

        for book in books:
            if book.id not in nums_of_reservations:
                nums_of_reservations.update({book.id: 0})

        for reservation in reservations:
            book_id = reservation.book_copy.book.id
            if date_empty:
                nums_of_reservations[book_id] += 1
            else:
                if reservation.start_date >= start_date and reservation.start_date <= end_date:
                    nums_of_reservations[book_id] += 1

        for book in books:
            book_infos.append({'title': book.title, 'num_of_reservations': nums_of_reservations[book.id]})

        return {'report': sorted(book_infos, key=lambda k: k['num_of_reservations'], reverse=True), 'template': 'most_often_reserved.html', 'error': False}

    ###

    elif report_type == u'black_list':
        nums_of_cancels = {}
        user_infos = []
        users = User.objects.all()
        reservations = Reservation.objects.filter(who_cancelled__isnull=False)
        date_empty = False

        if from_date == u'' or to_date == u'':
            date_empty = True
        else:
            try:
                [y, m, d] = map(int,from_date.split('-'))
                start_date = date(y, m, d)
                [y, m, d] = map(int,to_date.split('-'))
                end_date = date(y, m, d)
            except:
                return {'error': True, 'report': [], 'template': 'reports.html'}

        for user in users:
            if user.id not in nums_of_cancels:
                nums_of_cancels.update({user.id: 0})

        for reservation in reservations:
            user_id = reservation.for_whom.id
            if date_empty:
                nums_of_cancels[user_id] += 1
            else:
                if reservation.start_date >= start_date and reservation.start_date <= end_date:
                    nums_of_cancels[user_id] += 1

        for user in users:
            user_infos.append({'name': user.first_name + u' ' + user.last_name, 'num_of_cancels': nums_of_cancels[user.id]})

        return {'report': sorted(user_infos, key=lambda k: k['num_of_cancels'], reverse=True), 'template': 'black_list.html', 'error': False}

    ###

    elif report_type == u'lost_books':
        book_infos = get_report_data(u'status', u'', u'')['report']
        lost_books = filter(lambda b: b['status'] == 'Not available', book_infos)
        return {'report': lost_books, 'template': 'library_status.html', 'error': False}

    else:
        return {'report': [], 'template': 'reports.html', 'error': True}


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
    to_return = 0
    if book_copy.state.is_available == False:
        to_return = u'Not available'
    elif Rental.objects.filter(reservation__book_copy=book_copy).filter(end_date__isnull=True).count() > 0:
        to_return = u'Rented'
    elif Reservation.objects.filter(book_copy=book_copy).filter(end_date__isnull=True).count() > 0:
        to_return = u'Reserved'

    if to_return:
        return to_return
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
