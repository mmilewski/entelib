# -*- coding: utf-8 -*-

from views_aux import get_book_details, book_copy_status
from entelib.baseapp.models import Reservation, Rental, BookCopy, Book, User
from datetime import date, datetime
from baseapp.utils import pprint, order_asc_by_key, order_desc_by_key
import baseapp.utils as utils
from django.http import HttpResponse
import csv
from baseapp.views_aux import book_copies_status
from django.db.models.query_utils import Q
from copy import copy


def generate_csv(report_type, from_date, to_date, order_by=[]):
    """
    Desc:
        Returns csv file in HTTP response.

    Args:
        report_type  -- type of the report.
        from_date, to_date  -- describe the time period for the report.
        order_by  -- iterable. Names of parameters by which result should be ordered by.
                   Currently only one item is supported, bo using order_by will more 
                   then one element will take no effect. 

    Return:
        csv file in HTTP response.
    """

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=report.csv'
    writer = csv.writer(response)

    report_data = get_report_data(report_type, from_date, to_date, order_by=order_by)
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
            writer.writerow([   unicode(book['title']).encode('utf8'),
                                unicode(book['shelf_mark']).encode('utf8'),
                                unicode(book['location']).encode('utf8'),
                                unicode(book['status']).encode('utf8'),
                                unicode(book['for_whom']).encode('utf8'),
                                unicode(book['when']).encode('utf8'),
                                unicode(book['by_whom']).encode('utf8') ])

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


def get_report_data(report_type, from_date, to_date, order_by=[]):
    """
    Desc:
        Returns data for creating selected report.

    Args:
        report_type - basestring. type of the report
        from_date, to_date - basestring. describe the time period for the report.
        order_by - iterable. Names of parameters by which result should be ordered by.
                   Currently only one item is supported, bo using order_by will more 
                   then one element will take no effect. 

    Return:
        dict { 'report'   : report data
               'template' : template to be rendered (only filename. Proper dir will be attached elsewhere)
               'error'    : error message if sth goes wrong
               'ordering' : list of names used to sort report data
             }
    """
    assert from_date
    assert to_date
    order_by = list(order_by)
    order_by = order_by[:1] if order_by else []         # only one name can be used to order data 
    
    # NOTE: `ob` stands from order by
    ob_rename_dict = {'title'       : order_asc_by_key('title'),
                      '-title'      : order_desc_by_key('title'),
                      'location'    : order_asc_by_key('location_str'),
                      '-location'   : order_desc_by_key('location_str'),
                      'shelf_mark'  : order_asc_by_key('shelf_mark'),
                      '-shelf_mark' : order_desc_by_key('shelf_mark'),
                      'status'      : order_asc_by_key('status_str'),
                      '-status'     : order_desc_by_key('status_str'),
                      'for_whom'    : order_asc_by_key('for_whom'),
                      '-for_whom'   : order_desc_by_key('for_whom'),
                      'when'        : order_asc_by_key('when'),
                      '-when'       : order_desc_by_key('when'),
                      'librarian'   : order_asc_by_key('by_whom'),
                      '-librarian'  : order_desc_by_key('by_whom'),
                      'name'        : order_asc_by_key('name'),
                      '-name'       : order_desc_by_key('name'),
                      'num_cancels' : order_asc_by_key('num_of_cancels'),
                      '-num_cancels': order_desc_by_key('num_of_cancels'),
                      'num_rentals' : order_asc_by_key('num_of_rentals'),
                      '-num_rentals': order_desc_by_key('num_of_rentals'),
                      'num_rsvs'    : order_asc_by_key('num_of_reservations'),
                      '-num_rsvs'   : order_desc_by_key('num_of_reservations'),
                      }

    ob_in_status         = ['title', '-title', 'location', '-location', 'shelf_mark', '-shelf_mark', 
                            'status', '-status', 'for_whom', '-for_whom', 'when', '-when', 'librarian', '-librarian']
    ob_in_often_rented   = ['title', '-title', 'num_rentals', '-num_rentals']
    ob_in_often_reserved = ['title', '-title', 'num_rsvs', '-num_rsvs']
    ob_in_black_list     = ['name', '-name', 'num_cancels', '-num_cancels']
    ob_in_lost_books     = copy(ob_in_status)
    
    if report_type == u'status':
        book_infos = []
        copies = BookCopy.objects.select_related('id', 'state', 'book__title', 'location', 'location__building', 'shelf_mark')
        last_rentals = {}
        from datetime import timedelta, datetime
        status_day = utils.str_to_date(from_date, utils.today())
        status_day_start = datetime(status_day.year, status_day.month, status_day.day, 0, 0, 0)
        status_day_end = datetime(status_day.year, status_day.month, status_day.day, 23, 59, 59)
        
#         Q_start_date_filter =  Q(start_date__contains='')      # Q_all
#         if from_date:
#             Q_start_date_filter = Q(start_date__gte=from_date)
#         Q_end_date_filter = Q(end_date__isnull=True)
#         if to_date:
#             Q_end_date_filter = Q(end_date__lte=to_date) | Q(end_date__isnull=True)
#         rentals = Rental.objects.select_related('reservation', 'reservation__book_copy__id') \
#                                 .filter(Q_start_date_filter) \
#                                 .filter(Q_end_date_filter)
        Q_start_date_filter = Q(start_date__lte=status_day_end)
        Q_end_date_filter = (Q(end_date__isnull=True) | Q(end_date__gte=status_day_start))
        rentals = Rental.objects.select_related('reservation', 'reservation__book_copy__id') \
                                .filter(Q_start_date_filter) \
                                .filter(Q_end_date_filter)

        for rental in rentals:
            book_copy_id = rental.reservation.book_copy.id
            start_date = rental.start_date
            if book_copy_id not in last_rentals:
                last_rentals.update({book_copy_id: {'when'    : start_date,
                                                    'for_whom': rental.reservation.for_whom.first_name + u' ' +
                                                                rental.reservation.for_whom.last_name,
                                                    'by_whom' : rental.who_handed_out.first_name + u' ' +
                                                                rental.who_handed_out.last_name}})
            elif last_rentals[book_copy_id]['when'] < start_date:
                last_rentals.update({book_copy_id: {'when'    : start_date,
                                                    'for_whom': rental.reservation.for_whom.first_name + u' ' +
                                                                rental.reservation.for_whom.last_name,
                                                    'by_whom' : rental.who_handed_out.first_name + u' ' +
                                                                rental.who_handed_out.last_name}})

        book_infos = []
        statuses = book_copies_status(copies)
        for kopy in copies:
            copy_status = statuses[kopy.id]
            not_rented_yet = copy_status['copy'].id not in last_rentals
            if not_rented_yet:
                for_whom = when = by_whom = 'Not rented yet'
            else:
                last_rental = last_rentals[copy_status['copy'].id]
                (for_whom, when, by_whom) = (last_rental['for_whom'], last_rental['when'].date(), last_rental['by_whom'])            
            
            book_infos.append({ 'title'         : copy_status['copy'].book.title,
                                'shelf_mark'    : copy_status['copy'].shelf_mark,
                                'location'      : copy_status['copy'].location,
                                'location_str'  : unicode(copy_status['copy'].location).lower(),     # field for ordering purpose
                                'status'        : copy_status['status'],
                                'status_str'    : unicode(copy_status['status']).lower(),
                                'for_whom'      : for_whom,
                                'when'          : unicode(when),
                                'by_whom'       : by_whom,
                                'not_rented_yet': not_rented_yet})
        
        sort_by = list(set(order_by) & set(ob_in_status))
        if sort_by:
            book_infos.sort(cmp=ob_rename_dict[sort_by[0]])
        return {'report'   : book_infos, 
                'template' : 'library_status.html', 
                'error'    : False,
                'ordering' : sort_by,
                }

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

        sort_by = list(set(order_by) & set(ob_in_often_rented))
        if sort_by:
            book_infos.sort(cmp=ob_rename_dict[sort_by[0]])
        return {'report'   : book_infos, 
                'template' : 'most_often_rented.html', 
                'error'    : False,
                'ordering' : sort_by,
                }

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

        sort_by = list(set(order_by) & set(ob_in_often_reserved))
        if sort_by:
            book_infos.sort(cmp=ob_rename_dict[sort_by[0]])
        return {'report'   : book_infos, 
                'template' : 'most_often_reserved.html', 
                'error'    : False,
                'ordering' : sort_by,
                }

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

        sort_by = list(set(order_by) & set(ob_in_black_list))
        if sort_by:
            user_infos.sort(cmp=ob_rename_dict[sort_by[0]])

        return {'report'   : user_infos, 
                'template' : 'black_list.html', 
                'error'    : False,
                'ordering' : sort_by,
                }

    ###

    elif report_type == u'lost_books':
        reported_data = get_report_data(u'status', from_date, to_date)
        book_infos = reported_data['report']
        lost_books = filter(lambda b: not b['status'].is_available(), book_infos)
        sort_by = list(set(order_by) & set(ob_in_lost_books))
        if sort_by:
            lost_books.sort(cmp=ob_rename_dict[sort_by[0]])
        return {'report'   : lost_books, 
                'template' : 'unavailable_status.html', 
                'error'    : False,
                'ordering' : sort_by,
                }
    else:
        return {'report': [], 'template': 'reports.html', 'error': True}
